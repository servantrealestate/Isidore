from app.services.fetch_locations import fetch_locations_from_google_sheet
from app.services.process_locations import group_locations_by_county


async def run_property_services():
    sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"

    locations = await fetch_locations_from_google_sheet(sheet_url)
    group_locations_by_county(locations)
