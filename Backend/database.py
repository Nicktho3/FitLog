from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://localhost/fitlog"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)


