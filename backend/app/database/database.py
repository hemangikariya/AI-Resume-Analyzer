from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.settings import settings
from app.core.logger import logger

Base = declarative_base()

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    logger.info(f"Using SQLite database path: {db_url}")
    engine = create_engine(db_url, connect_args=connect_args)
else:
    logger.info("Configuring PostgreSQL database connection from settings.")
    engine = create_engine(db_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency injection provider for session database transactions.
    Ensures the connection closes immediately after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
