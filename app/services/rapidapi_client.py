import os
import logging
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("rapidapi_client.log")],
)

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

RAPIDAPI_HEADERS = {
    "x-rapidapi-key": RAPIDAPI_ZILLOW_API_KEY,
    "x-rapidapi-host": "zillow69.p.rapidapi.com",
}


class RateLimiter:
    def __init__(self, rate: int):
        self.rate = rate
        self.queue = asyncio.Queue()
        self.task = None

    async def start(self):
        while True:
            task, future = await self.queue.get()
            try:
                result = await task
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                await asyncio.sleep(1 / self.rate)  # Global rate limiting
                self.queue.task_done()

    async def add_task(self, task):
        future = asyncio.Future()
        await self.queue.put((task, future))
        if not self.task or self.task.done():
            self.task = asyncio.create_task(self._process_queue())
        return await future

    async def _process_queue(self):
        while not self.queue.empty():
            task, future = await self.queue.get()
            try:
                result = await task
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                await asyncio.sleep(1 / self.rate)  # Global rate limiting
                self.queue.task_done()
        self.task = None


# New function to fetch and check response status
async def fetch_with_status_check(session, url, headers, params):
    response = await session.get(url, headers=headers, params=params)
    if response.status != 200:
        logger.error(f"Error: Received status code {response.status} for URL: {url}")
        response_data = await response.text()
        raise Exception(
            f"Error: Received status code {response.status} for URL: {url}. Response: {response_data}"
        )
    return response
