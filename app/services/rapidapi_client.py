import aiohttp
import os
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
