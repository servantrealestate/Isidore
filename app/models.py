from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    Date,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    zpid = Column(Integer, unique=True)
    street_address = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    price = Column(Integer)
    currency = Column(String)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    living_area = Column(Float)
    living_area_units = Column(String)
    home_type = Column(String)
    home_status = Column(String)
    year_built = Column(Integer)
    description = Column(String)
    annual_homeowners_insurance = Column(Float)
    brokerage_name = Column(String)
    coming_soon_on_market_date = Column(Date)
    contingent_listing_type = Column(String)
    country = Column(String)
    county = Column(String)
    county_fips = Column(String)
    date_posted = Column(Date)
    date_sold = Column(Date)
    favorite_count = Column(Integer)
    is_listed_by_owner = Column(Boolean)
    listing_provider = Column(String)
    living_area_value = Column(Float)
    monthly_hoa_fee = Column(Float)
    page_view_count = Column(Integer)
    price_per_square_foot = Column(Float)
    property_tax_rate = Column(Float)
    rent_zestimate = Column(Integer)
    time_on_zillow = Column(String)
    timezone = Column(String)
    url = Column(String)
    zestimate = Column(Integer)
    zestimate_high_percent = Column(String)
    zestimate_low_percent = Column(String)

    address = relationship("Address", uselist=False, back_populates="property")
    price_history = relationship("PriceHistory", back_populates="property")
    schools = relationship("School", back_populates="property")
    tax_history = relationship("TaxHistory", back_populates="property")
    nearby_homes = relationship("NearbyHome", back_populates="property")
    mortgage_rates = relationship(
        "MortgageRates", uselist=False, back_populates="property"
    )
    reso_facts = relationship("ResoFacts", uselist=False, back_populates="property")
    solar_potential = relationship(
        "SolarPotential", uselist=False, back_populates="property"
    )


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    street_address = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    neighborhood = Column(String)

    property = relationship("Property", back_populates="address")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    date = Column(Date)
    price = Column(Integer)
    event = Column(String)
    price_per_square_foot = Column(Float)
    price_change_rate = Column(Float)
    source = Column(String)

    property = relationship("Property", back_populates="price_history")


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    name = Column(String)
    rating = Column(Integer)
    distance = Column(Float)
    level = Column(String)
    grades = Column(String)
    type = Column(String)
    size = Column(Integer)
    student_teacher_ratio = Column(Float)

    property = relationship("Property", back_populates="schools")


class TaxHistory(Base):
    __tablename__ = "tax_history"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    time = Column(Integer)
    tax_paid = Column(Float)
    tax_increase_rate = Column(Float)
    value = Column(Integer)
    value_increase_rate = Column(Float)

    property = relationship("Property", back_populates="tax_history")


class NearbyHome(Base):
    __tablename__ = "nearby_homes"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    zpid = Column(Integer)
    price = Column(Integer)
    street_address = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    home_status = Column(String)
    home_type = Column(String)

    property = relationship("Property", back_populates="nearby_homes")


class MortgageRates(Base):
    __tablename__ = "mortgage_rates"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    fifteen_year_fixed_rate = Column(Float)
    thirty_year_fixed_rate = Column(Float)
    arm5_rate = Column(Float)

    property = relationship("Property", back_populates="mortgage_rates")


class ResoFacts(Base):
    __tablename__ = "reso_facts"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    at_a_glance_facts = Column(JSON)
    other_facts = Column(JSON)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    bathrooms_full = Column(Integer)
    bathrooms_half = Column(Integer)
    cooling = Column(JSON)
    heating = Column(JSON)
    appliances = Column(JSON)
    laundry_features = Column(JSON)
    parking_features = Column(JSON)
    view = Column(JSON)
    lot_size = Column(String)
    home_type = Column(String)
    architecture_style = Column(String)
    year_built = Column(Integer)
    hoa_fee = Column(String)
    days_on_zillow = Column(Integer)

    property = relationship("Property", back_populates="reso_facts")


class SolarPotential(Base):
    __tablename__ = "solar_potential"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    sun_score = Column(Float)
    build_factor = Column(Float)
    climate_factor = Column(Float)
    electricity_factor = Column(Float)
    solar_factor = Column(Float)

    property = relationship("Property", back_populates="solar_potential")
