from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zpid = Column(Integer, unique=True, nullable=False)
    address = Column(String)
    unit = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    price = Column(Integer)
    price_change = Column(Integer)
    zestimate = Column(Integer)
    img_src = Column(String)
    detail_url = Column(String)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    living_area = Column(Float)
    lot_area_value = Column(Float)
    lot_area_unit = Column(String)
    listing_status = Column(String)
    property_type = Column(String)
    contingent_listing_type = Column(String)
    rent_zestimate = Column(Integer)
    days_on_zillow = Column(Integer)
    date_sold = Column(Date)
    country = Column(String)
    currency = Column(String)
    has_image = Column(Boolean)
