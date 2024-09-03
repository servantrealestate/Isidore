import pytest
from app.services.fetch_locations import fetch_locations_from_google_sheet
from app.services.process_locations import group_locations_by_zip


@pytest.mark.asyncio
async def test_group_locations_by_zip():
    sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"

    locations = await fetch_locations_from_google_sheet(sheet_url)
    zip_data = group_locations_by_zip(locations)

    assert isinstance(zip_data, dict)
    assert len(zip_data) > 0
    for zip_code, data in zip_data.items():
        assert "zip_code" in data
        assert "state_id" in data

    specific_zip = "90210"
    if specific_zip in zip_data:
        assert zip_data[specific_zip]["state_id"] == "CA"
        assert zip_data[specific_zip]["zip_code"] == "90210"
    else:
        pytest.fail(f"Zip code {specific_zip} not found in the data.")
