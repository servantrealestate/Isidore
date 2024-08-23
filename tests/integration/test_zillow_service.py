import os
import pytest
import aiohttp
from app.services.zillow_service import fetch_zillow_properties

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")


@pytest.mark.asyncio
async def test_fetch_zillow_properties():
    # Predefined location object
    location = {
        "county_name": "Lee",
        "state_name": "FL",
        "county_fips": "12071",
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

    # Ensure the API key is set
    assert RAPIDAPI_ZILLOW_API_KEY is not None, "RAPIDAPI_ZILLOW_API_KEY must be set"

    async with aiohttp.ClientSession() as session:
        properties = await fetch_zillow_properties(
            session,
            location=location["zipcodes"][0],  # Use the first zipcode for the query
            status_type="ForSale",
        )

    assert properties is not None, "Properties should not be None"
    assert isinstance(properties, list), "Properties should be a list"
    if properties:
        assert "zpid" in properties[0], "Each property should have a 'zpid' field"
        assert (
            "address" in properties[0]
        ), "Each property should have an 'address' field"

    print(
        f"Fetched {len(properties)} properties for location {location['zipcodes'][0]}"
    )


if __name__ == "__main__":
    pytest.main()
