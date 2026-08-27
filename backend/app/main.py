from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.authorization import router as authorization_router
from app.routers.students import router as students_router

app = FastAPI(title="Student Management System API")

app.include_router(auth_router)
app.include_router(authorization_router)
app.include_router(students_router)


@app.get("/")
def root():
    return {"message": "Student Management System Backend is running!"}
