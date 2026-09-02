from fastapi import FastAPI, Depends
from Backend import models
from Backend.database import engine, SessionLocal
from Backend.schemas import UserCreate
from sqlalchemy.orm import Session
from passlib.context import CryptContext

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application!"}
@app.get("/api/test")
def test_api():
    return {"message": "This is a test endpoint."}

@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=pwd_context.hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()