from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
import crud
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management API",
    description="REST API for managing student records",
    version="1.0.0"
)


@app.post(
    "/students",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db)
):
    existing_student = crud.get_student_by_email(db, email=student.email)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this email already exists"
        )
    return crud.create_student(db=db, student=student)


@app.get(
    "/students",
    response_model=List[schemas.StudentResponse],
    status_code=status.HTTP_200_OK
)
def read_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_students(db=db, skip=skip, limit=limit)


@app.get(
    "/students/{id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK
)
def read_student(
    id: int,
    db: Session = Depends(get_db)
):
    db_student = crud.get_student(db=db, student_id=id)
    if db_student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {id} not found"
        )
    return db_student


@app.put(
    "/students/{id}",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_200_OK
)
def update_student(
    id: int,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    db_student = crud.get_student(db=db, student_id=id)
    if db_student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {id} not found"
        )

    if student_update.email and student_update.email != db_student.email:
        existing_email = crud.get_student_by_email(db, email=student_update.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this email already exists"
            )

    return crud.update_student(db=db, student_id=id, student_update=student_update)


@app.delete(
    "/students/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_student(
    id: int,
    db: Session = Depends(get_db)
):
    deleted = crud.delete_student(db=db, student_id=id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {id} not found"
        )
    return None