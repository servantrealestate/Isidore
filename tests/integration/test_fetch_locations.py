import pytest
import aiohttp
from app.services.fetch_locations import fetch_locations_from_google_sheet


@pytest.mark.asyncio
async def test_fetch_locations_from_google_sheet():
    sheet_url = "https://docs.google.com/spreadsheets/d/1jGa8Y6UmdU1YAY2GbtKSNt80GggSkaEU5CvWAB2InBE/pub?gid=0&single=true&output=csv"

    locations = await fetch_locations_from_google_sheet(sheet_url)

    assert isinstance(locations, list)
    assert len(locations) > 0
    assert "county_name" in locations[0]
    assert "state_name" in locations[0]
