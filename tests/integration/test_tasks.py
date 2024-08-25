import pytest
from app.tasks import run_property_services


@pytest.mark.asyncio
async def test_run_property_services():
    test = await run_property_services()
    assert test is not None
