import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID")
    DATASET = os.getenv("BIGQUERY_DATASET")
    DATABASE_URL = f"bigquery://{PROJECT_ID}/{DATASET}"
else:
    DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
