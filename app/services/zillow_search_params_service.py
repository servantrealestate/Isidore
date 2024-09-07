import logging
import numpy as np
from app.services.rapidapi_client import RAPIDAPI_HEADERS

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log")],
)


async def get_zillow_total_results(
    location, status_type, session=None, rate_limiter=None, **kwargs
):
    logger.debug(f"Received kwargs: {kwargs}")
    url = "https://zillow69.p.rapidapi.com/search"
    querystring = {
        "location": location,
        "status_type": status_type,
        "home_type": "LotsLand",
        "soldInLast": kwargs.get("soldInLast", "") or "",
        "minPrice": kwargs.get("minPrice", "") or "",
        "maxPrice": kwargs.get("maxPrice", "") or "",
    }
    response = await rate_limiter.add_task(
        session.get(
            url,
            headers=RAPIDAPI_HEADERS,
            params=querystring,
        )
    )
    response_data = await response.json()
    if response_data.get("totalResultCount") is None:
        logger.error(
            f"Total result count is missing in the response data for location: {location}, status_type: {status_type}, kwargs: {kwargs}. Response data: {response_data}"
        )
        raise ValueError(
            f"Total result count is missing in the response data for location: {location}, status_type: {status_type}, kwargs: {kwargs}. Response data: {response_data}"
        )
    return response_data.get("totalResultCount")


async def get_min_price(
    location, status_type, session=None, rate_limiter=None, **kwargs
):
    url = "https://zillow69.p.rapidapi.com/search"
    querystring = {
        "location": location,
        "status_type": status_type,
        "home_type": "LotsLand",
        "soldInLast": kwargs.get("soldInLast", "") or "",
        "sort": "price_low_high",
        "minPrice": kwargs.get("minPrice", "") or "",
        "maxPrice": kwargs.get("maxPrice", "") or "",
    }
    response = await rate_limiter.add_task(
        session.get(
            url,
            headers=RAPIDAPI_HEADERS,
            params=querystring,
        )
    )
    response_data = await response.json()
    return response_data.get("props")[0].get("price")


async def get_max_price(
    location, status_type, session=None, rate_limiter=None, **kwargs
):
    url = "https://zillow69.p.rapidapi.com/search"
    querystring = {
        "location": location,
        "status_type": status_type,
        "home_type": "LotsLand",
        "soldInLast": kwargs.get("soldInLast", "") or "",
        "sort": "price_high_low",
        "minPrice": kwargs.get("minPrice", "") or "",
        "maxPrice": kwargs.get("maxPrice", "") or "",
    }
    response = await rate_limiter.add_task(
        session.get(
            url,
            headers=RAPIDAPI_HEADERS,
            params=querystring,
        )
    )
    response_data = await response.json()
    return response_data.get("props")[0].get("price")


async def split_price_query(
    location,
    status_type,
    min_price,
    max_price,
    fetch_params,
    session=None,
    rate_limiter=None,
    **kwargs,
):
    number_of_splits = 3
    price_splits = np.linspace(min_price, max_price, number_of_splits)
    price_splits = np.round(price_splits).astype(int)
    for i in range(number_of_splits - 1):
        min_price = max(int(price_splits[i]) - 1, 0)  # Ensure min_price is not negative
        max_price = int(price_splits[i + 1])
        total_results_for_price_range = await get_zillow_total_results(
            location,
            status_type,
            minPrice=min_price,
            maxPrice=max_price,
            soldInLast=kwargs.get("soldInLast", "") or "",
            session=session,
            rate_limiter=rate_limiter,
        )
        logger.info(
            f"Location: {location} | Status Type: {status_type} | Price Range: {min_price}-{max_price} | Total Results: {total_results_for_price_range}"
        )
        if total_results_for_price_range == 0:
            logger.warning(
                f"No results found for {location} with status_type {status_type} and soldInLast {kwargs.get('soldInLast', '')} and price range {min_price}-{max_price}"
            )
            continue
        elif total_results_for_price_range <= 820:
            fetch_params.append(
                {
                    "location": location,
                    "status_type": status_type,
                    "minPrice": min_price,
                    "maxPrice": max_price,
                    "soldInLast": kwargs.get("soldInLast", "") or "",
                }
            )
        else:
            logger.info(
                f"Total results for price range {min_price} to {max_price} is greater than 820, so we need to split the query again."
            )
            # TODO: address what happens if we've split the query down to where our max and min price are the same, and we still have more than 820 results.
            await split_price_query(
                location,
                status_type,
                min_price,
                max_price,
                fetch_params,
                soldInLast=kwargs.get("soldInLast", "") or "",
                session=session,
                rate_limiter=rate_limiter,
            )


async def get_zillow_search_params(
    zip_code, status_type, session=None, rate_limiter=None, **kwargs
):
    """
    Get the fetch parameters for Zillow API. There is a limit of 820 results per query, so if need be, this will split the query into multiple queries.
    """
    location = zip_code
    total_results = await get_zillow_total_results(
        location, status_type, **kwargs, session=session, rate_limiter=rate_limiter
    )
    if total_results is None:
        logger.warning(
            f"No results found for {location} with status_type {status_type} and sold_in_last {kwargs.get('soldInLast', '')}"
        )
        return None
    elif total_results == 0:
        logger.warning(
            f"No results found for {location} with status_type {status_type} and sold_in_last {kwargs.get('soldInLast', '')}"
        )
        return None
    logger.info(
        f"Location: {location} | Status Type: {status_type} | Sold In Last: {kwargs.get('soldInLast', '')} | Total Results: {total_results}"
    )
    fetch_params = []
    if total_results > 820:
        min_price = await get_min_price(
            location, status_type, **kwargs, session=session, rate_limiter=rate_limiter
        )
        max_price = await get_max_price(
            location, status_type, **kwargs, session=session, rate_limiter=rate_limiter
        )
        await split_price_query(
            location,
            status_type,
            min_price,
            max_price,
            fetch_params,
            **kwargs,
            session=session,
            rate_limiter=rate_limiter,
        )
    else:
        fetch_params.append(
            {
                "location": location,
                "status_type": status_type,
                "soldInLast": kwargs.get("soldInLast", "") or "",
            }
        )
    return fetch_params
