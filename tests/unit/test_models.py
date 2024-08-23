import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest  # noqa: F401
from app.models import Property
from app.db import SessionLocal


def test_create_property():
    db = SessionLocal()
    property = Property(street_address="123 Main St", price=100000)
    db.add(property)
    db.commit()

    assert property.id is not None
