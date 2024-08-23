from app.services.fetch_locations import fetch_locations_from_google_sheet
from app.services.location_processor import process_locations


async def run_property_services():
    sheet_url = "your_google_sheet_csv_url"

    locations = await fetch_locations_from_google_sheet(sheet_url)
    process_locations(locations)
