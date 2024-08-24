from app.services.fetch_locations import fetch_locations_from_google_sheet
from app.services.process_locations import group_locations_by_county
from app.services.zillow_service import get_zillow_fetch_params
import logging

logger = logging.getLogger(__name__)


async def run_property_services():
    sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"

    locations = await fetch_locations_from_google_sheet(sheet_url)
    counties = group_locations_by_county(locations)

    for county_fips, county_data in counties.items():
        # Get the queries for that location that will capture all the properties
        zillow_fetch_params = await get_zillow_fetch_params(county_data)
        # TODO: Search for properties for sale
        # TODO: Check if properties are in the database
        # TODO: Update properties in the database
        # TODO: Add properties to the database
