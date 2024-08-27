from app.db import SessionLocal
from app.models import Property
import logging

logger = logging.getLogger(__name__)


def get_or_create_property(property_data):
    session = SessionLocal()
    zpid = property_data["zpid"]
    db_property = session.query(Property).filter(Property.zpid == zpid).first()

    if db_property:
        # Update the property if necessary
        if db_property.price != property_data.get(
            "price"
        ) or db_property.home_status != property_data.get("home_status"):
            db_property.price = property_data.get("price")
            db_property.home_status = property_data.get("home_status")
            session.commit()
            logger.info(f"Updated property {zpid} in the database.")
    else:
        # Add the property to the database
        new_property = Property(
            zpid=property_data["zpid"],
            street_address=property_data.get("street_address"),
            city=property_data.get("city"),
            state=property_data.get("state"),
            zipcode=property_data.get("zipcode"),
            latitude=property_data.get("latitude"),
            longitude=property_data.get("longitude"),
            price=property_data.get("price"),
            currency=property_data.get("currency"),
            bedrooms=property_data.get("bedrooms"),
            bathrooms=property_data.get("bathrooms"),
            living_area=property_data.get("living_area"),
            living_area_units=property_data.get("living_area_units"),
            home_type=property_data.get("home_type"),
            home_status=property_data.get("home_status"),
            year_built=property_data.get("year_built"),
            description=property_data.get("description"),
            annual_homeowners_insurance=property_data.get(
                "annual_homeowners_insurance"
            ),
            brokerage_name=property_data.get("brokerage_name"),
            coming_soon_on_market_date=property_data.get("coming_soon_on_market_date"),
            contingent_listing_type=property_data.get("contingent_listing_type"),
            country=property_data.get("country"),
            county=property_data.get("county"),
            county_fips=property_data.get("county_fips"),
            date_posted=property_data.get("date_posted"),
            date_sold=property_data.get("date_sold"),
            favorite_count=property_data.get("favorite_count"),
            is_listed_by_owner=property_data.get("is_listed_by_owner"),
            listing_provider=property_data.get("listing_provider"),
            living_area_value=property_data.get("living_area_value"),
            monthly_hoa_fee=property_data.get("monthly_hoa_fee"),
            page_view_count=property_data.get("page_view_count"),
            price_per_square_foot=property_data.get("price_per_square_foot"),
            property_tax_rate=property_data.get("property_tax_rate"),
            rent_zestimate=property_data.get("rent_zestimate"),
            time_on_zillow=property_data.get("time_on_zillow"),
            timezone=property_data.get("timezone"),
            url=property_data.get("url"),
            zestimate=property_data.get("zestimate"),
            zestimate_high_percent=property_data.get("zestimate_high_percent"),
            zestimate_low_percent=property_data.get("zestimate_low_percent"),
        )
        session.add(new_property)
        session.commit()
        logger.info(f"Added new property {zpid} to the database.")

    session.close()
