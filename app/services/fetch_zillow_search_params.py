import aiohttp
import os
import numpy as np
import logging
import asyncio
import time
from aiohttp_client_cache import CachedSession, SQLiteBackend

logger = logging.getLogger(__name__)

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class RateLimiter:
    def __init__(self, rate, per):
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.monotonic()

    async def acquire(self):
        current = time.monotonic()
        time_passed = current - self.last_check
        self.last_check = current
        self.allowance += time_passed * (self.rate / self.per)

        if self.allowance > self.rate:
            self.allowance = self.rate

        if self.allowance < 1.0:
            await asyncio.sleep((1.0 - self.allowance) * (self.per / self.rate))
            self.allowance = 0
        else:
            self.allowance -= 1.0


rate_limiter = RateLimiter(4, 1)  # 4 requests per second


class RateLimitedSession:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        if ENVIRONMENT == "development":
            self.session = CachedSession(
                cache=SQLiteBackend("cache.sqlite", expire_after=86400),  # 24 hours
                *self.args,
                **self.kwargs,
            )
        else:
            self.session = aiohttp.ClientSession(*self.args, **self.kwargs)

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def get(self, *args, **kwargs):
        if ENVIRONMENT == "development":
            cache_key = self.session.cache.create_key(args[0], kwargs)
            if await self.session.cache.read(cache_key):
                logger.debug("Cache hit, skipping rate limiting")
                return await self.session.get(*args, **kwargs)
            else:
                logger.debug("Cache miss, applying rate limiting")
                await rate_limiter.acquire()
                return await self.session.get(*args, **kwargs)
        else:
            await rate_limiter.acquire()
            return await self.session.get(*args, **kwargs)


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
        min_price = int(price_splits[i]) - 1
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
