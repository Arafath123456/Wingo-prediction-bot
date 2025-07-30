from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

def get_engine():
    return create_engine(os.getenv("DATABASE_URL"), pool_size=10, max_overflow=20)

def get_session():
    engine = get_engine()
    return scoped_session(sessionmaker(bind=engine, autoflush=False))()

def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)