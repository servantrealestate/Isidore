import pytest
from app.services.fetch_locations import fetch_locations_from_google_sheet
from app.services.process_locations import group_locations_by_county


@pytest.mark.asyncio
async def test_group_locations_by_county():
    sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"

    locations = await fetch_locations_from_google_sheet(sheet_url)
    county_data = group_locations_by_county(locations)

    assert isinstance(county_data, dict)
    assert len(county_data) > 0
    for county_fips, data in county_data.items():
        assert "county_name" in data
        assert "state_id" in data

    specific_fips = "37183"
    if specific_fips in county_data:
        assert county_data[specific_fips]["state_id"] == "NC"
        assert county_data[specific_fips]["county_name"] == "Wake"
    else:
        pytest.fail(f"County with FIPS code {specific_fips} not found in the data.")
