import csv
import aiohttp


async def fetch_locations_from_google_sheet(sheet_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(sheet_url) as response:
            response_text = await response.text()
            reader = csv.DictReader(response_text.splitlines())
            locations = [row for row in reader]
    return locations
