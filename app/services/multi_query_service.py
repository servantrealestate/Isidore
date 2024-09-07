import os
import asyncio
import logging
from aiohttp import ClientSession, ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")


class SimpleRateLimiter:
    def __init__(self, rate: int):
        self.rate = rate
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            await asyncio.sleep(1 / self.rate)


async def fetch_url(session, url, params, rate_limiter):
    await rate_limiter.acquire()
    logger.info(f"Starting query for URL: {url}")
    headers = {
        "x-rapidapi-key": RAPIDAPI_ZILLOW_API_KEY,
        "x-rapidapi-host": "zillow69.p.rapidapi.com",
    }
    try:
        async with session.get(url, headers=headers, params=params) as response:
            response_data = await response.json()
            url_index = urls.index(url) + 1
            logger.info(
                f"Received response for URL {url_index}: {url} with status code: {response.status}"
            )
    except ClientError as e:
        logger.error(f"Error querying URL: {url}. Error: {str(e)}")


async def main(urls):
    rate_limiter = SimpleRateLimiter(rate=6)  # 7 requests per second
    async with ClientSession() as session:
        tasks = [fetch_url(session, url, {}, rate_limiter) for url in urls]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    urls = [
        "https://zillow69.p.rapidapi.com/search?location=90210&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=10001&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=94103&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=55118&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=23831&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=23075&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=23832&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=33793&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=35961&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=35962&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=35963&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=35967&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=35968&status_type=ForSale",
        "https://zillow69.p.rapidapi.com/search?location=35971&status_type=ForSale",
        # Add more URLs as needed
    ]
    asyncio.run(main(urls))
