from app.services.fetch_locations import fetch_locations_from_google_sheet
from app.services.process_locations import group_locations_by_county
from app.services.fetch_zillow_search_params import (
    get_zillow_search_params,
    check_total_zillow_results,
)
from app.services.fetch_zillow_properties import fetch_properties_for_params_list
from app.services.property_service import get_or_create_property
import logging
import asyncio

logger = logging.getLogger(__name__)


async def run_property_services():
    sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"

    locations = await fetch_locations_from_google_sheet(sheet_url)
    counties = group_locations_by_county(locations)

    for county_fips, county_data in counties.items():
        try:
            # Get the queries for that location that will capture all the properties
            zillow_search_params = await get_zillow_search_params(
                county_data, "ForSale"
            )
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

            for property_data in properties:
                get_or_create_property(property_data)
        except Exception as e:
            logger.error(
                f"An error occurred while processing {county_data['county_name']} County, {county_data['state_id']}: {e}"
            )
            continue

    return "Success"


if __name__ == "__main__":
    asyncio.run(run_property_services())
