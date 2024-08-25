from app.services.fetch_zillow_search_params import (
    get_zillow_search_params,
    check_total_zillow_results,
    check_min_price,
    check_max_price,
)
import pytest
import logging
import os

logger = logging.getLogger(__name__)


RAPIDAPI_ZILLOW_API_KEY = os.getenv("RAPIDAPI_ZILLOW_API_KEY")


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


@pytest.mark.asyncio
async def test_check_min_price():
    location = "Lee County, FL"
    status_type = "ForSale"
    sold_in_last = ""

    minPrice = await check_min_price(location, status_type, sold_in_last)

    assert isinstance(minPrice, int), "Min price should be an integer"
    assert minPrice >= 0, "Min price should be non-negative"
    # ASK: How do you structure an integration test that queries a live API? I am checking manually and then checking the debug value, but that's not a good test.


@pytest.mark.asyncio
async def test_check_max_price():
    location = "Lee County, FL"
    status_type = "ForSale"
    sold_in_last = ""

    maxPrice = await check_max_price(location, status_type, sold_in_last)

    assert isinstance(maxPrice, int), "Max price should be an integer"
    assert maxPrice >= 0, "Max price should be non-negative"
