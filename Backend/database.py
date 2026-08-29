from sqlalchemy import create_engine

DATABASE_URL = "postgresql://localhost/fitlog"

engine = create_engine(DATABASE_URL)

with engine.connect() as connection: 
    print("Connected to the database successfully!")
