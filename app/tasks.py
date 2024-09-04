from app.services.fetch_locations import fetch_locations_from_google_sheet
from app.services.process_locations import group_locations_by_zip
from app.services.fetch_zillow_search_params import get_zillow_search_params
from app.services.fetch_zillow_properties import fetch_properties_for_params_list
from app.services.fetch_zillow_search_params import check_total_zillow_results
from app.services.property_service import get_or_create_properties
import logging
import asyncio
from tqdm.asyncio import tqdm

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log")],
)


async def process_zip(zip_code, zip_data, status_type, soldInLast=None):
    try:
        zillow_search_params = await get_zillow_search_params(
            zip_code, status_type, soldInLast=soldInLast
        )
        if not zillow_search_params:
            logger.warning(
                f"No results found for {zip_code} with status_type {status_type} and soldInLast {soldInLast}"
            )
            return

        properties = await fetch_properties_for_params_list(zillow_search_params)
        total_results = await check_total_zillow_results(
            zip_code, status_type, soldInLast=soldInLast
        )

        logger.info(
            f"Location: {zip_code} | Status: {status_type} | Sold in Last: {soldInLast} | Expected Properties: {total_results} | Actual Properties: {len(properties)}"
        )

        for property in properties:
            property["zip_code"] = zip_code
            property["state_id"] = zip_data["state_id"]

        get_or_create_properties(properties)
    except Exception as e:
        logger.error(f"{status_type} properties for {zip_code}: {e}")


async def run_property_services():
    # Test URL
    sheet_url = "https://docs.google.com/spreadsheets/d/1WZMtAdgJCLo9pFAhBsszCRPZZDMX16Xtt25er92F48E/pub?output=csv"
    # Production URL
    # sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"
    # Define the state_ids we want to filter by

    # Fetch locations from Google Sheet
    locations = await fetch_locations_from_google_sheet(sheet_url)

    # Group filtered locations by zip code
    zip_codes = group_locations_by_zip(locations)

    semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent tasks

    async def sem_process_zip(zip_code, zip_data, status_type, soldInLast=None):
        async with semaphore:
            await process_zip(zip_code, zip_data, status_type, soldInLast)

    # Process Sold properties
    sold_tasks = [
        sem_process_zip(zip_code, zip_data, "RecentlySold", soldInLast="90")
        for zip_code, zip_data in zip_codes.items()
    ]
    await tqdm.gather(*sold_tasks, desc="Processing Sold Properties")

    # Process ForSale properties
    for_sale_tasks = [
        sem_process_zip(zip_code, zip_data, "ForSale")
        for zip_code, zip_data in zip_codes.items()
    ]
    await tqdm.gather(*for_sale_tasks, desc="Processing For Sale Properties")

    return "Success"


if __name__ == "__main__":
    asyncio.run(run_property_services())
