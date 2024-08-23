from app.services.fetch_locations import fetch_locations_from_google_sheet
from app.services.process_locations import group_locations_by_county
from app.services.zillow_service import (
    search_properties,
    get_property_details,
    update_property_in_db,
    check_and_update_properties,
    add_property_to_db,
    property_in_db,
)


async def run_property_services():
    sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"

    locations = await fetch_locations_from_google_sheet(sheet_url)
    group_locations_by_county(locations)

    for location in locations:
        # Search for properties for sale
        properties_for_sale = await search_properties(
            location, property_type="for_sale"
        )
        for property in properties_for_sale:
            details = await get_property_details(property["id"])
            if property_in_db(property["id"]):
                await update_property_in_db(details)
            else:
                await add_property_to_db(details)

        # Search for recently sold properties
        recently_sold_properties = await search_properties(
            location, property_type="recently_sold"
        )
        for property in recently_sold_properties:
            details = await get_property_details(property["id"])
            if property_in_db(property["id"]):
                await update_property_in_db(details)
            else:
                await add_property_to_db(details)

        await check_and_update_properties(location)
