from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application!"}
@app.get("/api/test")
def test_api():
    return {"message": "This is a test endpoint."}