import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"))
load_dotenv() # Fallback to cwd

# The application requires a NeonDB (PostgreSQL) connection string
# with pg8000 driver. E.g. postgresql+pg8000://user:password@host/dbname
# For tests or local development, a default could be used, or just require the env var.
# We'll use a placeholder for now to allow alembic init without error if not set,
# but it must be set for real operations.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# In production/NeonDB, ssl_context or ssl arguments might be needed depending on the driver.
# pg8000 requires ssl_context=True for SSL connections.
connect_args = {}
if "pg8000" in DATABASE_URL:
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl_context"] = ssl_context
elif "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL, 
    echo=False,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
