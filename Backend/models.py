"""SQLAlchemy classes describe the tables stored in the database."""
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from Backend.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class LoginSession(Base):
    __tablename__ = "login_sessions"
    token_hash = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(Float, nullable=False)


class Food(Base):
    __tablename__ = "foods"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    name = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)


class Workout(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    exercise = Column(String, nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)


class Goal(Base):
    __tablename__ = "goals"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    calories = Column(Float, nullable=False, default=2000)
    protein = Column(Float, nullable=False, default=150)
    carbs = Column(Float, nullable=False, default=250)
    fat = Column(Float, nullable=False, default=65)
