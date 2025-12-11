# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database file (will be created in the project folder)
DATABASE_URL = "sqlite:///university_mis.db"

# The engine is the connection to the database
engine = create_engine(
    DATABASE_URL,
    echo=True,        # prints SQL queries in the terminal (useful for learning)
    future=True
)

# Session factory: we will use this to talk to the DB from our code
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

# Base class for all our models (tables)
Base = declarative_base()
