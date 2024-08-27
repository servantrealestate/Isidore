import logging
import numpy as np
from app.services.rapidapi_client import RateLimitedSession, RAPIDAPI_ZILLOW_API_KEY

logger = logging.getLogger(__name__)


async def check_total_zillow_results(location, status_type, sold_in_last="", **kwargs):
    logger.debug(f"Received kwargs: {kwargs}")
    url = "https://zillow69.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_ZILLOW_API_KEY,
        "X-RapidAPI-Host": "zillow69.p.rapidapi.com",
    }
    querystring = {
        "location": location,
        "status_type": status_type,
        "home_type": "LotsLand",
        "soldInLast": sold_in_last,
        "minPrice": kwargs.get("minPrice", ""),
        "maxPrice": kwargs.get("maxPrice", ""),
    }
    async with RateLimitedSession() as session:
        async with session.get(url, headers=headers, params=querystring) as response:
            response_data = await response.json()
            return response_data.get("totalResultCount")


async def check_min_price(location, status_type, sold_in_last="", **kwargs):
    url = "https://zillow69.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_ZILLOW_API_KEY,
        "X-RapidAPI-Host": "zillow69.p.rapidapi.com",
    }
    querystring = {
        "location": location,
        "status_type": status_type,
        "home_type": "LotsLand",
        "soldInLast": sold_in_last,
        "sort": "price_low_high",
        "minPrice": kwargs.get("minPrice", ""),
        "maxPrice": kwargs.get("maxPrice", ""),
    }
    async with RateLimitedSession() as session:
        async with session.get(url, headers=headers, params=querystring) as response:
            response_data = await response.json()
            return response_data.get("props")[0].get("price")


async def check_max_price(location, status_type, sold_in_last="", **kwargs):
    url = "https://zillow69.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_ZILLOW_API_KEY,
        "X-RapidAPI-Host": "zillow69.p.rapidapi.com",
    }
    querystring = {
        "location": location,
        "status_type": status_type,
        "home_type": "LotsLand",
        "soldInLast": sold_in_last,
        "sort": "price_high_low",
        "minPrice": kwargs.get("minPrice", ""),
        "maxPrice": kwargs.get("maxPrice", ""),
    }
    async with RateLimitedSession() as session:
        async with session.get(url, headers=headers, params=querystring) as response:
            response_data = await response.json()
            return response_data.get("props")[0].get("price")


async def split_query(location, status_type, min_price, max_price, fetch_params):
    number_of_splits = 10
    price_splits = np.linspace(min_price, max_price, number_of_splits)
    price_splits = np.round(price_splits).astype(int)
    for i in range(number_of_splits - 1):
        min_price = max(int(price_splits[i]) - 1, 0)  # Ensure min_price is not negative
        max_price = int(price_splits[i + 1])
        total_results_for_price_range = await check_total_zillow_results(
            location, status_type, minPrice=min_price, maxPrice=max_price
        )
        logger.info(
            f"Location: {location} | Price Range: {min_price}-{max_price} | Total Results: {total_results_for_price_range}"
        )
        if total_results_for_price_range <= 400:
            fetch_params.append(
                {
                    "location": location,
                    "status_type": status_type,
                    "minPrice": min_price,
                    "maxPrice": max_price,
                }
            )
        else:
            logger.info(
                f"Total results for price range {min_price} to {max_price} is greater than 400, so we need to split the query again."
            )
            # TODO: address what happens if we've split the query down to where our max and min price are the same, and we still have more than 400 results.
            await split_query(location, status_type, min_price, max_price, fetch_params)


async def get_zillow_search_params(county, status_type):
    """
    Get the fetch parameters for Zillow API. There is a limit of 400 results per query, so if need be, this will split the query into multiple queries.
    """
    location = f"{county['county_name']} County, {county['state_id']}"
    total_results = await check_total_zillow_results(location, status_type)
    logger.info(f"Location: {location} | Total Results: {total_results}")
    fetch_params = []
    if total_results > 400:
        min_price = await check_min_price(location, status_type)
        max_price = await check_max_price(location, status_type)
        await split_query(location, status_type, min_price, max_price, fetch_params)
    else:
        fetch_params.append(
            {
                "location": location,
                "status_type": status_type,
            }
        )
    return fetch_params
