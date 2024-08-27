import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest  # noqa: F401
from app.models import Property
from app.db import SessionLocal


def test_create_property():
    db = SessionLocal()
    property = Property(
        zpid=2054254952,
        address="Vic Ave #D4-42, Lancaster, CA 93535",
        unit="# D4-42",
        latitude=34.77348,
        longitude=-118.05653,
        price=8000,
        price_change=-500,
        zestimate=None,
        img_src="https://photos.zillowstatic.com/fp/480f3eb800ceb70f51dbe124f17126a7-p_e.jpg",
        detail_url="/homedetails/Vic-Ave-D4-42-Lancaster-CA-93535/2054254952_zpid/",
        bedrooms=None,
        bathrooms=None,
        lot_area_value=2.56,
        lot_area_unit="acres",
        listing_status="FOR_SALE",
        property_type="LOT",
        contingent_listing_type=None,
        rent_zestimate=2136,
        days_on_zillow=278,
        date_sold=None,
        country="USA",
        currency="USD",
        has_image=True,
    )
    db.add(property)
    db.commit()

    assert property.id is not None
