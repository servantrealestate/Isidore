from app.db import engine, ENVIRONMENT
from app.models import Base, Property  # NOQA: F401
from sqlalchemy import text

# Check database connection
try:
    with engine.connect() as connection:
        print("Database connection successful.")
        if ENVIRONMENT == "development":
            result = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            )
        else:
            result = connection.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
                )
            )
        tables = result.fetchall()
        print(f"Existing tables before creation: {tables}")
except Exception as e:
    print(f"Database connection failed: {e}")

# Drop all tables
try:
    Base.metadata.drop_all(engine)
    print("Existing tables dropped successfully.")
except Exception as e:
    print(f"Error dropping tables: {e}")

# Create all tables
try:
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
    with engine.connect() as connection:
        if ENVIRONMENT == "development":
            result = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            )
        else:
            result = connection.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
                )
            )
        tables = result.fetchall()
        print(f"Existing tables after creation: {tables}")
except Exception as e:
    print(f"Error creating tables: {e}")
