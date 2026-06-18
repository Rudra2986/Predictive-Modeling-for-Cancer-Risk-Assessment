from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from backend.utils.config import settings

# Determine connection URL and configuration
DATABASE_URL = settings.DATABASE_URL
engine_args = {"pool_pre_ping": True}

try:
    # Attempt to initialize and connect to PostgreSQL
    engine = create_engine(DATABASE_URL, **engine_args)
    # Quick test connection ping
    with engine.connect() as conn:
        pass
    print("Database: Successfully connected to PostgreSQL.")
except (OperationalError, Exception) as e:
    if settings.ENVIRONMENT == "production":
        print(f"CRITICAL DATABASE ERROR: Production database connection failed: {e}")
        raise e
    print("Database Warning: Local PostgreSQL server is unreachable. Falling back to local SQLite database (oncorisk.db).")
    DATABASE_URL = "sqlite:///oncorisk.db"
    engine_args = {"connect_args": {"check_same_thread": False}}
    engine = create_engine(DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base model meta-class for declarative tables
Base = declarative_base()

# Dependency generator to retrieve DB sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
