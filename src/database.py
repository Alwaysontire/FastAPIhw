from sqlalchemy import create_engine, Column, Integer, String, DateTime, desc, or_
from sqlalchemy.orm import declarative_base, sessionmaker, Session


DATABASE_URL = "sqlite:///.tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()