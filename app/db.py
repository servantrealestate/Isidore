import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    DATABASE_URL = "sqlite:///./test.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
