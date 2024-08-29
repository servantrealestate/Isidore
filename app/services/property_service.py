from google.cloud import bigquery
import logging
import os
import re
from google.api_core.exceptions import NotFound
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def get_or_create_properties(properties_data):
    logger.info("Starting get_or_create_properties")
    client = bigquery.Client()
    project_id = os.getenv("BIGQUERY_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET")
    table_id = f"{project_id}.{dataset_id}.properties"
    rows_to_insert = []

    logger.info(
        f"Project ID: {project_id}, Dataset ID: {dataset_id}, Table ID: {table_id}"
    )

    # Check if table exists, create if not
    try:
        client.get_table(table_id)
    except NotFound:
        logger.info(f"Table {table_id} not found. Creating table.")
        schema = [
            bigquery.SchemaField("id", "INTEGER"),
            bigquery.SchemaField("zpid", "INTEGER"),
            bigquery.SchemaField("address", "STRING"),
            bigquery.SchemaField("unit", "STRING"),
            bigquery.SchemaField("latitude", "FLOAT"),
            bigquery.SchemaField("longitude", "FLOAT"),
            bigquery.SchemaField("price", "FLOAT"),
            bigquery.SchemaField("price_change", "FLOAT"),
            bigquery.SchemaField("zestimate", "FLOAT"),
            bigquery.SchemaField("img_src", "STRING"),
            bigquery.SchemaField("detail_url", "STRING"),
            bigquery.SchemaField("bedrooms", "FLOAT"),
            bigquery.SchemaField("bathrooms", "FLOAT"),
            bigquery.SchemaField("living_area", "FLOAT"),
            bigquery.SchemaField("lot_area_value", "FLOAT"),
            bigquery.SchemaField("lot_area_unit", "STRING"),
            bigquery.SchemaField("listing_status", "STRING"),
            bigquery.SchemaField("property_type", "STRING"),
            bigquery.SchemaField("contingent_listing_type", "STRING"),
            bigquery.SchemaField("rent_zestimate", "FLOAT"),
            bigquery.SchemaField("days_on_zillow", "FLOAT"),
            bigquery.SchemaField("date_sold", "DATE"),
            bigquery.SchemaField("country", "STRING"),
            bigquery.SchemaField("currency", "STRING"),
            bigquery.SchemaField("has_image", "BOOLEAN"),
            bigquery.SchemaField("county_name", "STRING"),
            bigquery.SchemaField("state_id", "STRING"),
            bigquery.SchemaField("county_fips", "STRING"),
            bigquery.SchemaField("zip_code", "STRING"),
        ]
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)
        logger.info(f"Table {table_id} created successfully.")

    # Collect all zpids
    zpids = [int(property_data["zpid"]) for property_data in properties_data]
    zpid_str = ", ".join(map(str, zpids))

    # Batch query to get all properties at once
    query = f"SELECT * FROM `{table_id}` WHERE zpid IN ({zpid_str})"
    query_job = client.query(query)
    results = {row["zpid"]: row for row in query_job.result()}

    for property_data in properties_data:
        zpid = int(property_data["zpid"])
        if zpid in results:
            db_property = results[zpid]
            # Update the property if necessary
            if db_property["price"] != property_data.get("price") or db_property[
                "listing_status"
            ] != property_data.get("listingStatus"):
                update_query = f"""
                UPDATE `{table_id}`
                SET price = {property_data.get("price")},
                    listing_status = '{property_data.get("listingStatus")}',
                    price_change = {property_data.get("priceChange")},
                    zestimate = {property_data.get("zestimate")},
                    img_src = '{property_data.get("imgSrc")}',
                    detail_url = '{property_data.get("detailUrl")}',
                    bedrooms = {property_data.get("bedrooms")},
                    bathrooms = {property_data.get("bathrooms")},
                    living_area = {property_data.get("livingArea")},
                    lot_area_value = {property_data.get("lotAreaValue")},
                    lot_area_unit = '{property_data.get("lotAreaUnit")}',
                    contingent_listing_type = '{property_data.get("contingentListingType")}',
                    rent_zestimate = {property_data.get("rentZestimate")},
                    days_on_zillow = {property_data.get("daysOnZillow")},
                    date_sold = '{datetime.fromtimestamp(
                        property_data.get("dateSold") / 1000, timezone.utc
                    ).strftime("%Y-%m-%d")}',
                    country = '{property_data.get("country")}',
                    currency = '{property_data.get("currency")}',
                    has_image = {property_data.get("hasImage")}
                WHERE zpid = {zpid}
                """
                client.query(update_query)
        else:
            # Parse zip code from address using regex
            address = property_data.get("address", "")
            zip_code_match = re.search(r"\b\d{5}\b$", address)
            zip_code = zip_code_match.group(0) if zip_code_match else None

            rows_to_insert.append(
                {
                    "id": zpid,
                    "zpid": zpid,
                    "address": property_data.get("address"),
                    "unit": property_data.get("unit"),
                    "latitude": property_data.get("latitude"),
                    "longitude": property_data.get("longitude"),
                    "price": property_data.get("price"),
                    "price_change": property_data.get("priceChange"),
                    "zestimate": property_data.get("zestimate"),
                    "img_src": property_data.get("imgSrc"),
                    "detail_url": f"https://www.zillow.com{property_data.get('detailUrl')}",
                    "bedrooms": property_data.get("bedrooms"),
                    "bathrooms": property_data.get("bathrooms"),
                    "living_area": property_data.get("livingArea"),
                    "lot_area_value": property_data.get("lotAreaValue"),
                    "lot_area_unit": property_data.get("lotAreaUnit"),
                    "listing_status": property_data.get("listingStatus"),
                    "property_type": property_data.get("propertyType"),
                    "contingent_listing_type": property_data.get(
                        "contingentListingType"
                    ),
                    "rent_zestimate": property_data.get("rentZestimate"),
                    "days_on_zillow": property_data.get("daysOnZillow"),
                    "date_sold": datetime.fromtimestamp(
                        property_data.get("dateSold") / 1000, timezone.utc
                    ).strftime("%Y-%m-%d"),
                    "country": property_data.get("country"),
                    "currency": property_data.get("currency"),
                    "has_image": property_data.get("hasImage"),
                    "county_name": property_data.get("county_name"),
                    "state_id": property_data.get("state_id"),
                    "county_fips": property_data.get("county_fips"),
                    "zip_code": zip_code,
                }
            )
            logger.info(f"Added property with zpid {zpid} to rows_to_insert")
    if rows_to_insert:
        logger.info(f"Inserting {len(rows_to_insert)} new properties")
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            logger.error(f"Errors occurred while inserting rows: {errors}")
        else:
            logger.info(
                f"Inserted {len(rows_to_insert)} new properties into the database."
            )
    logger.info("Completed get_or_create_properties")
