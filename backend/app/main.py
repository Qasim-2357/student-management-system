from fastapi import FastAPI

app = FastAPI(title="Student Management System")


@app.get("/")
def root():
    return {"message": "Student Management System API"}