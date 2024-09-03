import logging
import asyncio
from app.tasks import (
    process_county,
    fetch_locations_from_google_sheet,
    group_locations_by_county,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log")],
)


def find_county_by_name_and_state(counties, county_name, state_id):
    county_name = county_name.replace("County", "").strip()
    for fips, county_data in counties.items():
        if (
            county_data["county_name"] == county_name
            and county_data["state_id"] == state_id
        ):
            return fips, county_data
    return None, None


async def debug_county(counties, county_name, state_id, status_type, soldInLast=None):
    county_fips, county_data = find_county_by_name_and_state(
        counties, county_name, state_id
    )
    if county_data:
        await process_county(county_fips, county_data, status_type, soldInLast)
    else:
        logger.error(f"County {county_name}, {state_id} not found.")


async def run_debugging():
    # Test URL
    # sheet_url = "https://docs.google.com/spreadsheets/d/1WZMtAdgJCLo9pFAhBsszCRPZZDMX16Xtt25er92F48E/pub?output=csv"
    # Production URL
    sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"

    locations = await fetch_locations_from_google_sheet(sheet_url)
    counties = group_locations_by_county(locations)

    # List of problematic counties
    problematic_counties = [
        {"county_name": "Lee", "state_id": "FL"},
        # Add more problematic counties here
    ]

    for county in problematic_counties:
        await debug_county(
            counties,
            county["county_name"],
            county["state_id"],
            "RecentlySold",
            soldInLast="90",
        )
        await debug_county(
            counties, county["county_name"], county["state_id"], "ForSale"
        )

    return "Debugging Complete"


if __name__ == "__main__":
    asyncio.run(run_debugging())
