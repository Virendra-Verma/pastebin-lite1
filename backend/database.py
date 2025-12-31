from sqlalchemy import create_engine, Column, String, Integer, BigInteger, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

def get_database_url():
    # Prefer Vercel Neon Postgres when available
    postgres_url = (
        os.getenv("POSTGRES_URL_NON_POOLING") or 
        os.getenv("DATABASE_URL_UNPOOLED") or 
        os.getenv("POSTGRES_URL") or 
        os.getenv("DATABASE_URL")
    )
    if postgres_url:
        print(f"Using Postgres database: {postgres_url.split('@')[1] if '@' in postgres_url else 'Postgres detected'}")
        return postgres_url
    
    # Fallback to SQLite for local development
    _is_vercel = os.getenv("VERCEL") == "1"
    sqlite_path = "sqlite:////tmp/pastes.db" if _is_vercel else "sqlite:///./pastes.db"
    print(f"Using SQLite database: {sqlite_path}")
    return sqlite_path

DATABASE_URL = get_database_url()

# Use NullPool for serverless (Postgres), SQLite needs special args
if "postgresql" in DATABASE_URL:
    from sqlalchemy.pool import NullPool
    engine = create_engine(DATABASE_URL, poolclass=NullPool)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Paste(Base):
    __tablename__ = "pastes"
    
    id = Column(String(8), primary_key=True, index=True)
    content = Column(Text, nullable=False)
    expires_at = Column(BigInteger, nullable=True)  # Unix timestamp in milliseconds
    max_views = Column(Integer, nullable=True)
    views = Column(Integer, default=0)
    created_at = Column(BigInteger, nullable=False)  # Unix timestamp in milliseconds
    is_expired = Column(Boolean, default=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Drop and recreate table to update schema (temporary fix)
    if "postgresql" in DATABASE_URL:
        Paste.__table__.drop(engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
