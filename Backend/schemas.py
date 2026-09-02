from pydantic import BaseModel

class UserCreate(BaseModel):
    id: int
    email: str
    username: str
  