from app.services.fetch_locations import fetch_locations_from_google_sheet
from app.services.process_locations import group_locations_by_county
from app.services.fetch_zillow_search_params import (
    get_zillow_search_params,
    check_total_zillow_results,
)
from app.services.fetch_zillow_properties import fetch_properties_for_params_list
from app.services.property_service import get_or_create_properties
import logging
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


async def run_property_services():
    # Test URL
    sheet_url = "https://docs.google.com/spreadsheets/d/1WZMtAdgJCLo9pFAhBsszCRPZZDMX16Xtt25er92F48E/pub?output=csv"
    # Production URL
    # sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"

    locations = await fetch_locations_from_google_sheet(sheet_url)
    counties = group_locations_by_county(locations)

    # Get Sold properties
    for county_fips, county_data in counties.items():
        try:
            # Get the queries for that location that will capture all the properties
            zillow_search_params = await get_zillow_search_params(
                county_data, "RecentlySold", sold_in_last="90"
            )
            if not zillow_search_params:
                logger.warning(
                    f"No results found for {county_data['county_name']} County, {county_data['state_id']} with status_type RecentlySold and sold_in_last 90"
                )
                continue
            properties = await fetch_properties_for_params_list(zillow_search_params)
            for property in properties:
                property["county_name"] = county_data["county_name"]
                property["state_id"] = county_data["state_id"]
                property["county_fips"] = county_fips

            get_or_create_properties(properties)
        except Exception as e:
            logger.error(
                f"Sold properties for {county_data['county_name']} County, {county_data['state_id']}: {e}"
            )
            continue

    # Get ForSale properties
    for county_fips, county_data in counties.items():
        try:
            # Get the queries for that location that will capture all the properties
            zillow_search_params = await get_zillow_search_params(
                county_data, "ForSale"
            )
            if not zillow_search_params:
                logger.warning(
                    f"No results found for {county_data['county_name']} County, {county_data['state_id']} with status_type RecentlySold and sold_in_last 90"
                )
                continue
            properties = await fetch_properties_for_params_list(zillow_search_params)

            # Verify the totalResultCount matches the total number of properties returned
            total_results = await check_total_zillow_results(
                f"{county_data['county_name']} County, {county_data['state_id']}",
                "ForSale",
            )
            if total_results != len(properties):
                logger.warning(
                    f"Total results ({total_results}) do not match the number of properties fetched ({len(properties)}) for {county_data['county_name']} County, {county_data['state_id']}"
                )
            else:
                logger.info(
                    f"{county_data['county_name']} County, {county_data['state_id']}: Total results ({total_results}) match properties fetched ({len(properties)})"
                )

            # Pass county_name and state_id to get_or_create_properties
            for property in properties:
                property["county_name"] = county_data["county_name"]
                property["state_id"] = county_data["state_id"]
                property["county_fips"] = county_fips

            get_or_create_properties(properties)
        except Exception as e:
            logger.error(
                f"For Sale properties for {county_data['county_name']} County, {county_data['state_id']}: {e}"
            )
            continue

    return "Success"


if __name__ == "__main__":
    asyncio.run(run_property_services())
