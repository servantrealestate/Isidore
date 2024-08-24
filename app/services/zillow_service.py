import aiohttp
import os
import asyncio

import logging

logger = logging.getLogger(__name__)

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")


async def get_zillow_fetch_params(county, status_type):
    """
    Get the fetch parameters for Zillow API. There is a limit of 400 results per query, so if need be, this will split the query into multiple queries.
    """
    total_results = await check_total_zillow_results(
        f"{county['county_name']} County, {county['state_id']}", status_type
    )
    fetch_params = []
    if total_results > 400:
        for zipcode in county["zipcodes"]:
            zipcode_results = await check_total_zillow_results(zipcode, status_type)
            if zipcode_results > 400:
                # If there are more than 400 results, we need to split the results into price ranges.
                price_splits = [
                    [0, 100000],
                    [100000, 200000],
                    [200000, 300000],
                    [300000, 400000],
                    [400000, 500000],
                    [500000, 600000],
                    [600000, 700000],
                    [700000, 800000],
                    [800000, 900000],
                    [900000, 1000000],
                    [1000000, ""],
                ]
                for price_split in price_splits:
                    min_price = price_split[0]
                    max_price = price_split[1]
                    price_split_results = await check_total_zillow_results(
                        zipcode,
                        status_type,
                        minPrice=min_price,
                        maxPrice=max_price,
                    )
                    if price_split_results > 400:
                        logger.warning(
                            f"More than 400 results for price range {min_price} - {max_price} in zipcode {zipcode}."
                        )
                        continue
                    else:
                        fetch_params.append(
                            {
                                "location": zipcode,
                                "status_type": status_type,
                                "minPrice": min_price,
                                "maxPrice": max_price,
                            }
                        )
            else:
                fetch_params.append(
                    {
                        "location": zipcode,
                        "status_type": status_type,
                    }
                )
    else:
        fetch_params.append(
            {
                "location": f"{county['county_name']}, {county['state_id']}",
                "status_type": status_type,
            }
        )
    return fetch_params


async def check_total_zillow_results(location, status_type, sold_in_last="", **kwargs):
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
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=querystring) as response:
            response_data = await response.json()
            return response_data.get("totalResultCount")


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
