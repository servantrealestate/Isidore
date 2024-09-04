import logging
import re
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Property

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log")],
)


def get_or_create_properties(properties_data):
    zip_code = properties_data[0]["zip_code"]
    state_id = properties_data[0]["state_id"]
    listing_status = properties_data[0]["listingStatus"]
    number_of_properties = len(properties_data)
    logger.info(
        f"Zip Code: {zip_code}, State ID: {state_id}, Listing Status: {listing_status}, Number of Properties: {number_of_properties}"
    )
    db: Session = SessionLocal()
    try:
        for property_data in properties_data:
            zpid = int(property_data["zpid"])
            db_property = db.query(Property).filter(Property.zpid == zpid).first()
            if db_property:
                # Update the property if necessary
                if db_property.price != property_data.get(
                    "price"
                ) or db_property.listing_status != property_data.get("listingStatus"):
                    db_property.price = property_data.get("price")
                    db_property.listing_status = property_data.get("listingStatus")
                    db_property.price_change = property_data.get("priceChange")
                    db_property.zestimate = property_data.get("zestimate")
                    db_property.img_src = property_data.get("imgSrc")
                    db_property.detail_url = property_data.get("detailUrl")
                    db_property.bedrooms = property_data.get("bedrooms")
                    db_property.bathrooms = property_data.get("bathrooms")
                    db_property.living_area = property_data.get("livingArea")
                    db_property.lot_area_value = property_data.get("lotAreaValue")
                    db_property.lot_area_unit = property_data.get("lotAreaUnit")
                    db_property.contingent_listing_type = property_data.get(
                        "contingentListingType"
                    )
                    db_property.rent_zestimate = property_data.get("rentZestimate")
                    db_property.days_on_zillow = property_data.get("daysOnZillow")
                    db_property.date_sold = (
                        datetime.fromtimestamp(
                            property_data.get("dateSold") / 1000, timezone.utc
                        ).date()
                        if property_data.get("dateSold")
                        else None
                    )
                    db_property.country = property_data.get("country")
                    db_property.currency = property_data.get("currency")
                    db_property.has_image = property_data.get("hasImage")
                    db_property.county_name = property_data.get("county_name")
                    db_property.state_id = property_data.get("state_id")
                    db_property.county_fips = property_data.get("county_fips")
                    db_property.zip_code = (
                        re.search(
                            r"\b\d{5}\b$", property_data.get("address", "")
                        ).group(0)
                        if re.search(r"\b\d{5}\b$", property_data.get("address", ""))
                        else None
                    )
                    db.commit()
            else:
                new_property = Property(
                    zpid=zpid,
                    address=property_data.get("address"),
                    unit=property_data.get("unit"),
                    latitude=property_data.get("latitude"),
                    longitude=property_data.get("longitude"),
                    price=property_data.get("price"),
                    price_change=property_data.get("priceChange"),
                    zestimate=property_data.get("zestimate"),
                    img_src=property_data.get("imgSrc"),
                    detail_url=f"https://www.zillow.com{property_data.get('detailUrl')}",
                    bedrooms=property_data.get("bedrooms"),
                    bathrooms=property_data.get("bathrooms"),
                    living_area=property_data.get("livingArea"),
                    lot_area_value=property_data.get("lotAreaValue"),
                    lot_area_unit=property_data.get("lotAreaUnit"),
                    listing_status=property_data.get("listingStatus"),
                    property_type=property_data.get("propertyType"),
                    contingent_listing_type=property_data.get("contingentListingType"),
                    rent_zestimate=property_data.get("rentZestimate"),
                    days_on_zillow=property_data.get("daysOnZillow"),
                    date_sold=datetime.fromtimestamp(
                        property_data.get("dateSold") / 1000, timezone.utc
                    ).date()
                    if property_data.get("dateSold")
                    else None,
                    country=property_data.get("country"),
                    currency=property_data.get("currency"),
                    has_image=property_data.get("hasImage"),
                    county_name=property_data.get("county_name"),
                    state_id=property_data.get("state_id"),
                    county_fips=property_data.get("county_fips"),
                    zip_code=re.search(
                        r"\b\d{5}\b$", property_data.get("address", "")
                    ).group(0)
                    if re.search(r"\b\d{5}\b$", property_data.get("address", ""))
                    else None,
                )
                db.add(new_property)
                db.commit()
        number_of_properties_check = (
            db.query(Property)
            .filter(
                Property.zip_code == zip_code, Property.listing_status == listing_status
            )
            .count()
        )
        logger.info(
            f"Zip Code: {zip_code}, State ID: {state_id}, Listing Status: {listing_status}, Num of Properties to Check or Write: {number_of_properties}, Num of Properties Checked or Written: {number_of_properties_check}"
        )
        if number_of_properties > number_of_properties_check:
            logger.error(
                f"Zip Code: {zip_code}, State ID: {state_id}, Listing Status: {listing_status}, Number of properties to check or write: {number_of_properties} greater than number of properties checked or written: {number_of_properties_check}. There may have been a write error."
            )
    except Exception as e:
        logger.error(f"Error in get_or_create_properties: {e}")
    finally:
        db.close()
