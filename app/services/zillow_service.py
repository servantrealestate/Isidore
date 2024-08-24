import aiohttp
import os
import asyncio

import logging

logger = logging.getLogger(__name__)

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")


async def fetch_zillow_properties(
    session, location, status_type, sold_in_last="", **kwargs
):
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
        "lotSizeMin": kwargs.get("lotSizeMin", ""),
        "lotSizeMax": kwargs.get("lotSizeMax", ""),
        "soldInLast": sold_in_last,
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
        async with session.get(url, headers=headers, params=querystring) as response:
            try:
                response_data = await response.json()
                properties.extend(response_data.get("props", []))
                total_pages = response_data.get("totalPages", 1)
            except Exception as e:
                print(f"Error processing response: {e}")
                break

            print(
                f"{status_type} | {response.status} | {location} | Page {current_page} of {total_pages}"
            )

        current_page += 1
        await asyncio.sleep(0.5)  # To avoid hitting rate limits

    return properties


async def search_properties(location, property_type, filters=None):
    """
    Search for properties in a given location.
    If there are more than 400 results, apply filters to reduce the count.

    :param location: The location to search properties in.
    :param property_type: The type of properties to search for ('for_sale' or 'recently_sold').
    :param filters: Optional filters to apply to the search.
    """
    async with aiohttp.ClientSession() as session:
        if property_type == "for_sale":
            return await fetch_zillow_properties(
                session, location, status_type="ForSale", **(filters or {})
            )
        elif property_type == "recently_sold":
            return await fetch_zillow_properties(
                session,
                location,
                status_type="RecentlySold",
                sold_in_last="12",
                **(filters or {}),
            )
        else:
            raise ValueError(
                "Invalid property_type. Must be 'for_sale' or 'recently_sold'."
            )


async def get_property_details(property_id):
    """
    Get details of an individual property by its ID.
    """
    # Implement the logic to query Zillow API for property details
    pass


async def update_property_in_db(property):
    """
    Update property details in the database if they have changed.
    """
    # Implement the logic to update property details in the database
    pass


async def check_and_update_properties(location):
    """
    Check properties in the database for a given location and update their status.
    """
    # Implement the logic to check and update properties in the database
    pass


async def add_property_to_db(property):
    """
    Add a new property to the database.
    """
    # Implement the logic to add a new property to the database
    pass


def property_in_db(property_id):
    """
    Check if a property is already in the database.
    """
    # Implement the logic to check if a property is in the database
    pass
