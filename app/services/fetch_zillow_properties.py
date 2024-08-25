import logging
from app.services.rapidapi_client import RateLimitedSession, RAPIDAPI_ZILLOW_API_KEY

logger = logging.getLogger(__name__)


async def fetch_zillow_properties(location, status_type, sold_in_last="", **kwargs):
    url = "https://zillow69.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_ZILLOW_API_KEY,
        "X-RapidAPI-Host": "zillow69.p.rapidapi.com",
    }

    querystring = {
        "location": location,
        "status_type": status_type,
        "home_type": "LotsLand",
        "minPrice": kwargs.get("minPrice", ""),
        "maxPrice": kwargs.get("maxPrice", ""),
        "soldInLast": sold_in_last,
    }

    # Add any additional parameters from kwargs
    for key, value in kwargs.items():
        if key not in querystring:
            querystring[key] = value

    properties = []
    current_page = 1
    total_pages = 1

    async with RateLimitedSession() as session:
        while current_page <= total_pages:
            querystring["page"] = current_page
            async with session.get(
                url, headers=headers, params=querystring
            ) as response:
                try:
                    response_data = await response.json()
                    properties.extend(response_data.get("props", []))
                    total_pages = response_data.get("totalPages", 1)
                except Exception as e:
                    logger.error(f"Error processing response: {e}")
                    break

                logger.info(
                    f"{status_type} | {response.status} | {location} | Page {current_page} of {total_pages} | MinPrice: {querystring.get('minPrice', 'N/A')} | MaxPrice: {querystring.get('maxPrice', 'N/A')}"
                )

                current_page += 1

    return properties


async def fetch_properties_for_params_list(params_list):
    all_properties = []
    for params in params_list:
        properties = await fetch_zillow_properties(**params)
        all_properties.extend(properties)
    return all_properties
