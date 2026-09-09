"""FitLog API and frontend, served together from one origin."""
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from Backend import models, schemas
from Backend.auth import COOKIE, current_user, hash_password, start_session, token_hash, verify_password
from Backend.database import engine, get_db


@asynccontextmanager
async def lifespan(app):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="FitLog", lifespan=lifespan, redoc_url=None)
FRONTEND = Path(__file__).resolve().parent.parent / "Frontend"


@app.middleware("http")
async def security_headers(request: Request, call_next):
    # JSON-only mutations plus Strict cookies prevent cross-site form submissions.
    if request.method in {"POST", "PUT", "DELETE"}:
        if request.headers.get("content-type", "").split(";")[0] != "application/json":
            return JSONResponse({"detail": "Use application/json."}, status_code=415)
        if request.headers.get("sec-fetch-site") == "cross-site":
            return JSONResponse({"detail": "Cross-site requests are not allowed."}, status_code=403)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    if request.url.path in {"/docs", "/docs/oauth2-redirect"}:
        # FastAPI's generated Swagger page loads its UI from this CDN.
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; img-src 'self' data: https://fastapi.tiangolo.com; frame-ancestors 'none'; base-uri 'none'"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/register", response_model=schemas.UserResponse, status_code=201)
def register(data: schemas.UserCreate, response: Response, db: Session = Depends(get_db)):
    user = models.User(email=data.email, username=data.username, hashed_password=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email or username already registered.")
    db.refresh(user)
    db.add(models.Goal(user_id=user.id))
    start_session(response, user.id, db)
    return user


@app.post("/api/login", response_model=schemas.UserResponse)
def login(data: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Email or password is incorrect.")
    if db.get(models.Goal, user.id) is None:
        db.add(models.Goal(user_id=user.id))
    start_session(response, user.id, db)
    return user


@app.post("/api/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(COOKIE)
    if token:
        db.query(models.LoginSession).filter_by(token_hash=token_hash(token)).delete()
        db.commit()
    response.delete_cookie(COOKIE)


@app.get("/api/me", response_model=schemas.UserResponse)
def me(user=Depends(current_user)):
    return user


@app.get("/api/day")
def day(date: date, user=Depends(current_user), db: Session = Depends(get_db)):
    foods = db.query(models.Food).filter_by(user_id=user.id, date=date).order_by(models.Food.id).all()
    workouts = db.query(models.Workout).filter_by(user_id=user.id, date=date).order_by(models.Workout.id).all()
    goals = db.get(models.Goal, user.id)
    return {
        "foods": [schemas.FoodResponse.model_validate(food) for food in foods],
        "workouts": [schemas.WorkoutResponse.model_validate(workout) for workout in workouts],
        "totals": {key: round(sum(getattr(food, key) for food in foods), 2)
                   for key in ("calories", "protein", "carbs", "fat")},
        "goals": schemas.GoalInput.model_validate(goals),
    }


@app.put("/api/goals", response_model=schemas.GoalInput)
def update_goals(data: schemas.GoalInput, user=Depends(current_user), db: Session = Depends(get_db)):
    goal = db.get(models.Goal, user.id)
    for key, value in data.model_dump().items():
        setattr(goal, key, value)
    db.commit()
    db.refresh(goal)
    return goal


@app.post("/api/foods", response_model=schemas.FoodResponse, status_code=201)
def add_food(data: schemas.FoodCreate, user=Depends(current_user), db: Session = Depends(get_db)):
    food = models.Food(user_id=user.id, **data.model_dump())
    db.add(food)
    db.commit()
    db.refresh(food)
    return food


@app.post("/api/workouts", response_model=schemas.WorkoutResponse, status_code=201)
def add_workout(data: schemas.WorkoutCreate, user=Depends(current_user), db: Session = Depends(get_db)):
    workout = models.Workout(user_id=user.id, **data.model_dump())
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@app.delete("/api/{kind}/{entry_id}", status_code=204)
def delete_entry(kind: str, entry_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    table = {"foods": models.Food, "workouts": models.Workout}.get(kind)
    if table is None:
        raise HTTPException(404, "Entry not found.")
    entry = db.query(table).filter_by(id=entry_id, user_id=user.id).first()
    if entry is None:
        raise HTTPException(404, "Entry not found.")
    db.delete(entry)
    db.commit()


@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
