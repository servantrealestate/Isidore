import os
from google.cloud import bigquery
from app.db import engine, ENVIRONMENT
from app.models import Base, Property  # NOQA: F401
from sqlalchemy import text

# Initialize BigQuery client
client = bigquery.Client()

# Define your dataset and table names
project_id = os.getenv("BIGQUERY_PROJECT_ID")  # Ensure this is set correctly
dataset_id = os.getenv("BIGQUERY_DATASET")  # Use environment variable for dataset ID
table_id = "properties"

# Debug prints to check environment variables
print(f"Project ID: {project_id}")
print(f"Dataset ID: {dataset_id}")

# Check if dataset exists
try:
    dataset_ref = client.dataset(dataset_id)
    client.get_dataset(dataset_ref)  # Make an API request.
    print(f"Dataset {dataset_id} found.")
except Exception as e:
    print(f"Dataset {dataset_id} not found: {e}")
    exit(1)

# Check database connection
try:
    with engine.connect() as connection:
        print("Database connection successful.")
        query = f"SELECT table_name FROM `{dataset_id}.INFORMATION_SCHEMA.TABLES`"
        result = connection.execute(text(query))
        tables = result.fetchall()
        print(f"Existing tables before creation: {tables}")
except Exception as e:
    print(f"Database connection failed: {e}")

# Drop all tables
try:
    table_ref = client.dataset(dataset_id).table(table_id)
    client.delete_table(table_ref, not_found_ok=True)
    print("Existing tables dropped successfully.")
except Exception as e:
    print(f"Error dropping tables: {e}")

# Create all tables
try:
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
    with engine.connect() as connection:
        query = f"SELECT table_name FROM `{dataset_id}.INFORMATION_SCHEMA.TABLES`"
        result = connection.execute(text(query))
        tables = result.fetchall()
        print(f"Existing tables after creation: {tables}")
except Exception as e:
    print(f"Error creating tables: {e}")
