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
        assert "zipcodes" in data
        assert isinstance(data["zipcodes"], list)
        assert len(data["zipcodes"]) > 0

    specific_fips = "37183"
    if specific_fips in county_data:
        assert len(county_data[specific_fips]["zipcodes"]) == 32
        expected_zipcodes = [
            "27502",
            "27511",
            "27513",
            "27518",
            "27519",
            "27529",
            "27539",
            "27540",
            "27545",
            "27560",
            "27571",
            "27587",
            "27591",
            "27592",
            "27597",
            "27601",
            "27603",
            "27604",
            "27605",
            "27606",
            "27607",
            "27608",
            "27609",
            "27610",
            "27612",
            "27613",
            "27614",
            "27615",
            "27616",
            "27617",
            "27695",
            "27697",
        ]
        assert sorted(county_data[specific_fips]["zipcodes"]) == sorted(
            expected_zipcodes
        )
    else:
        pytest.fail(f"County with FIPS code {specific_fips} not found in the data.")
