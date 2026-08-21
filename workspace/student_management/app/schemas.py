from typing import Optional
from pydantic import BaseModel, EmailStr


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    age: int
    grade: str


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    grade: Optional[str] = None


class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True