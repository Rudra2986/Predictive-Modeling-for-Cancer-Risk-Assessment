from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.utils.config import settings

# Create engine
# pool_pre_ping=True helps prevent connection drops
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

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
