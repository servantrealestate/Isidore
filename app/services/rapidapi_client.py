import os
import logging
import asyncio
import time
from aiohttp import ClientSession, ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class RateLimiter:
    def __init__(self, rate: int, per: float):
        self.rate = rate
        self.per = per
        self.semaphore = asyncio.Semaphore(1)
        self.last_request_time = 0

    async def acquire(self):
        async with self.semaphore:
            now = time.monotonic()
            time_since_last_request = now - self.last_request_time
            if time_since_last_request < self.per:
                wait_time = self.per - time_since_last_request
                logger.warning(
                    f"Rate limit reached. Waiting for {wait_time:.2f} seconds..."
                )
                await asyncio.sleep(wait_time)
            self.last_request_time = time.monotonic()
            logger.info(
                f"Request allowed. Time since last request: {time_since_last_request:.2f} seconds"
            )


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
        logger.info(f"Fetching URL: {url}, params: {params}")
        try:
            await self.rate_limiter.acquire()
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

    async def __aenter__(self):
        await self.ensure_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
