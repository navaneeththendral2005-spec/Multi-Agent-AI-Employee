from fastapi import FastAPI
from app.database import engine, Base
from app.routers import students

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management API",
    description="A FastAPI application for managing student records using SQLite",
    version="1.0.0"
)

app.include_router(students.router)


@app.get("/")
def root():
    return {"message": "Welcome to the Student Management API"}