import logging
from app.services.rapidapi_client import RAPIDAPI_HEADERS, fetch_with_status_check

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log")],
)


async def fetch_zillow_properties(
    location, status_type, session=None, rate_limiter=None, **kwargs
):
    url = "https://zillow69.p.rapidapi.com/search"

    querystring = {
        "location": location,
        "status_type": status_type,
        "home_type": "LotsLand",
        "minPrice": kwargs.get("minPrice", ""),
        "maxPrice": kwargs.get("maxPrice", ""),
        "soldInLast": kwargs.get("soldInLast", ""),
    }

    # Add any additional parameters from kwargs
    for key, value in kwargs.items():
        if key not in querystring:
            querystring[key] = value

    properties = []
    current_page = 1
    total_pages = 1

    while current_page <= total_pages:
        querystring["page"] = current_page
        try:
            response = await rate_limiter.add_task(
                fetch_with_status_check(session, url, RAPIDAPI_HEADERS, querystring)
            )
            response_data = await response.json()
            properties.extend(response_data.get("props", []))
            total_pages = response_data.get("totalPages", 0)
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            break

        logger.info(
            f"{status_type} | Page {current_page} of {total_pages} | MinPrice: {querystring.get('minPrice', 'N/A')} | MaxPrice: {querystring.get('maxPrice', 'N/A')} | SoldInLast: {querystring.get('soldInLast', 'N/A')}"
        )

        current_page += 1

    return properties


async def fetch_properties_for_params_list(
    params_list, session=None, rate_limiter=None
):
    all_properties = []
    for params in params_list:
        properties = await fetch_zillow_properties(
            session=session, rate_limiter=rate_limiter, **params
        )
        all_properties.extend(properties)
    return all_properties
