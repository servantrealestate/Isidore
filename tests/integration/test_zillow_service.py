import os
import pytest
import aiohttp
from app.services.zillow_service import fetch_zillow_properties

RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")


@pytest.mark.asyncio
async def test_fetch_zillow_properties():
    # Predefined location object
    location = {
        "county_name": "Durham",
        "state_name": "NC",
        "county_fips": "37063",
        "zipcodes": [
            "27503",
            "27701",
            "27703",
            "27704",
            "27705",
            "27707",
            "27708",
            "27709",
            "27712",
            "27713",
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
