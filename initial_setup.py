import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy_utils import database_exists, create_database
from app.db import engine, DATABASE_URL
from app.models import Base

# Create the database if it doesn't exist
if not database_exists(engine.url):
    try:
        # Connect to PostgreSQL server
        psql_conn = psycopg2.connect(
            dbname="postgres", user="work", host="localhost", password=""
        )
        psql_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        psql_cursor = psql_conn.cursor()

        # Create the database
        psql_cursor.execute("CREATE DATABASE properties")

        psql_cursor.close()
        psql_conn.close()

        print("Database 'properties' created successfully.")
    except Exception as e:
        print(f"Error creating database: {e}")
        exit(1)

# Now proceed with table creation
try:
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
except Exception as e:
    print(f"Error creating tables: {e}")
