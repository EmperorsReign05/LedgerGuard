import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The application requires a NeonDB (PostgreSQL) connection string
# with pg8000 driver. E.g. postgresql+pg8000://user:password@host/dbname
# For tests or local development, a default could be used, or just require the env var.
# We'll use a placeholder for now to allow alembic init without error if not set,
# but it must be set for real operations.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# In production/NeonDB, ssl_context or ssl arguments might be needed depending on the driver.
# pg8000 usually handles ssl natively if 'sslmode=require' is in the URL.
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    # connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
