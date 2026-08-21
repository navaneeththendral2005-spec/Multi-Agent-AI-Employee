from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    age: int
    grade: Optional[str] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    grade: Optional[str] = None


class StudentResponse(StudentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)