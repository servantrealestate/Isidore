import os
import logging
import asyncio
import time
from aiohttp import ClientSession, ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log")],
)

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class RateLimiter:
    def __init__(self, rate: int, per: float):
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.last_refill_time = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.monotonic()
            if self.tokens <= 1:
                wait_time = self.per
                logger.warning(
                    f"Rate limit reached. Waiting for {wait_time:.2f} seconds..."
                )
                await asyncio.sleep(wait_time)

            self.tokens -= 1
            return now

    async def release(self, acquire_time):
        async with self.lock:
            now = time.monotonic()
            time_since_acquire = now - acquire_time

            # Refill the token bucket
            new_tokens = time_since_acquire * (self.rate / self.per)
            self.tokens = min(self.rate, self.tokens + new_tokens)
            self.last_refill_time = now


class RateLimitedSession:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        self.session = None

    async def ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = ClientSession()

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch(self, url: str, params: dict):
        await self.ensure_session()
        headers = {
            "x-rapidapi-key": RAPIDAPI_ZILLOW_API_KEY,
            "x-rapidapi-host": "zillow69.p.rapidapi.com",
        }
        logger.debug(f"Fetching URL: {url}, params: {params}")
        try:
            acquire_time = await self.rate_limiter.acquire()
            async with self.session.get(
                url, headers=headers, params=params
            ) as response:
                if response.status == 429:
                    logger.error("Rate limit reached (HTTP 429)")
                    raise Exception("Rate limit reached")
                response_data = await response.json()
                return response_data
        except ClientError as e:
            logger.error(f"Error fetching URL: {url}. Error: {str(e)}")
            raise
        finally:
            await self.rate_limiter.release(acquire_time)

    async def __aenter__(self):
        await self.ensure_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
