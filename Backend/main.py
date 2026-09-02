from fastapi import FastAPI
from Backend import models
from Backend.database import engine, SessionLocal
from Backend.schemas import UserCreate

models.Base.metadata.create_all(bind=engine)

app = FastAPI()



@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application!"}
@app.get("/api/test")
def test_api():
    return {"message": "This is a test endpoint."}

@app.post("/users")
def create_user(user: UserCreate):
    return user