import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

# Defaults to a local SQLite file so this runs with zero setup.
# For production, set DATABASE_URL to a hosted Postgres instance, e.g.:
#   postgresql://user:password@host:5432/dbname
# Free Postgres hosts that work well here: Neon (neon.tech) or Supabase.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./draft_board.db")
# Hosts typically hand out a plain "postgresql://" URL; normalize it to use the psycopg3 driver.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Prospect(Base):
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)
    rank = Column(Integer, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    position = Column(String(10), nullable=False)
    school = Column(String(120), nullable=False)
    note = Column(String(500), nullable=False, default="")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


def init_db():
    Base.metadata.create_all(bind=engine)
