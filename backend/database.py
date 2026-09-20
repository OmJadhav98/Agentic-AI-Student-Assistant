import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# -----------------------------
# Load Environment Variables
# -----------------------------

load_dotenv()


# -----------------------------
# Database Configuration
# -----------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set."
    )


# -----------------------------
# Database Engine
# -----------------------------

engine = create_engine(
    DATABASE_URL
)


# -----------------------------
# Database Session
# -----------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# -----------------------------
# SQLAlchemy Base
# -----------------------------

Base = declarative_base()