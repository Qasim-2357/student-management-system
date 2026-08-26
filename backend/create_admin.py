from app.database import SessionLocal
from app.models.models import User
from app.security import hash_password


db = SessionLocal()

admin = User(
    name="System Admin",
    email="admin@example.com",
    password_hash=hash_password("Admin@123"),
    role="admin"
)

db.add(admin)
db.commit()
db.close()

print("Admin created successfully.")