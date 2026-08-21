from typing import List, Optional
from sqlalchemy.orm import Session
import models
import schemas


def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.email == email).first()


def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[models.Student]:
    return db.query(models.Student).offset(skip).limit(limit).all()


def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(
        name=student.name,
        email=student.email,
        age=student.age,
        grade=student.grade,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(
    db: Session, student_id: int, student_update: schemas.StudentUpdate
) -> Optional[models.Student]:
    db_student = get_student(db, student_id)
    if not db_student:
        return None

    update_data = student_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> bool:
    db_student = get_student(db, student_id)
    if not db_student:
        return False

    db.delete(db_student)
    db.commit()
    return True