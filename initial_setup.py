from app.db import engine
from app.models import (
    Base,
    Property,  # noqa: F401
    Address,  # noqa: F401
    PriceHistory,  # noqa: F401
    School,  # noqa: F401
    TaxHistory,  # noqa: F401
    NearbyHome,  # noqa: F401
    MortgageRates,  # noqa: F401
    ResoFacts,  # noqa: F401
    SolarPotential,  # noqa: F401
)
from sqlalchemy import text

# Check database connection
try:
    with engine.connect() as connection:
        print("Database connection successful.")
        result = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table';")
        )
        tables = result.fetchall()
        print(f"Existing tables before creation: {tables}")
except Exception as e:
    print(f"Database connection failed: {e}")

# Create all tables
try:
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table';")
        )
        tables = result.fetchall()
        print(f"Existing tables after creation: {tables}")
except Exception as e:
    print(f"Error creating tables: {e}")
