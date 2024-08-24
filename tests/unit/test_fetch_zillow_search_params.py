from app.services.fetch_zillow_search_params import (
    get_zillow_search_params,
    check_total_zillow_results,
)
import pytest
import aiohttp
import os

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")


@pytest.mark.asyncio
async def test_get_zillow_search_params():
    county = {
        "county_name": "Lee",
        "state_id": "FL",
        "zipcodes": [
            "33901",
            "33903",
            "33904",
            "33905",
            "33907",
            "33908",
            "33909",
            "33912",
            "33913",
            "33914",
            "33916",
            "33917",
            "33919",
            "33920",
            "33921",
            "33922",
            "33924",
            "33928",
            "33931",
            "33956",
            "33957",
            "33965",
            "33966",
            "33967",
            "33971",
            "33972",
            "33973",
            "33974",
            "33976",
            "33990",
            "33991",
            "33993",
            "34134",
            "34135",
        ],
    }
    status_type = "ForSale"
    async with aiohttp.ClientSession() as session:
        search_params = await get_zillow_search_params(county, status_type, session)

        assert isinstance(search_params, dict), "Search params should be a dictionary"
        assert "location" in search_params, "Location should be in search params"
        assert "status_type" in search_params, "Status type should be in search params"
        assert "home_type" in search_params, "Home type should be in search params"
        assert "soldInLast" in search_params, "Sold in last should be in search params"


@pytest.mark.asyncio
async def test_check_total_zillow_results():
    location = "Lee County, FL"
    status_type = "ForSale"
    sold_in_last = ""

    # Ensure the API key is set
    assert RAPIDAPI_ZILLOW_API_KEY is not None, "RAPIDAPI_ZILLOW_API_KEY must be set"

    totalResultCount = await check_total_zillow_results(
        location, status_type, sold_in_last
    )

    assert isinstance(totalResultCount, int), "Total results should be an integer"
    assert totalResultCount >= 0, "Total results should be non-negative"

    print(f"Total results for location {location}: {totalResultCount}")
