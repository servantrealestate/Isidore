import aiohttp
import os
import asyncio

import logging

logger = logging.getLogger(__name__)

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")


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
    async with aiohttp.ClientSession() as session:
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
    async with aiohttp.ClientSession() as session:
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
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=querystring) as response:
            response_data = await response.json()
            return response_data.get("props")[0].get("price")


async def get_zillow_search_params(county, status_type):
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
                    [0, 99999],
                    [100000, 199999],
                    [200000, 299999],
                    [300000, 399999],
                    [400000, 499999],
                    [500000, 599999],
                    [600000, 699999],
                    [700000, 799999],
                    [800000, 899999],
                    [900000, 999999],
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
