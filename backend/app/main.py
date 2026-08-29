from fastapi import FastAPI
from app.routers.attendance import router as attendance_router
from app.routers.auth import router as auth_router
from app.routers.authorization import router as authorization_router
from app.routers.classes import router as classes_router
from app.routers.students import router as students_router
from app.routers.subjects import router as subjects_router
from app.routers.teachers import router as teachers_router
from app.routers.exams import router as exams_router
from app.routers.marks import router as marks_router
from app.routers.grades import router as grades_router

app = FastAPI(title="Student Management System API")

app.include_router(auth_router)
app.include_router(authorization_router)
app.include_router(students_router)
app.include_router(teachers_router)
app.include_router(classes_router)
app.include_router(subjects_router)
app.include_router(attendance_router)
app.include_router(exams_router)
app.include_router(marks_router)
app.include_router(grades_router)

@app.get("/")
def root():
    return {"message": "Student Management System Backend is running!"}