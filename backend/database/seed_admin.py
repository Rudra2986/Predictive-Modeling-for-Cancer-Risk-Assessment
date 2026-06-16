import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from backend.database.session import SessionLocal
from backend.database.base import User
from backend.utils.security import hash_password

def seed_admin_user():
    print("Database seeding: checking/creating default admin user...")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@oncorisk.ai")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_password:
        print("Database seeding Warning: ADMIN_PASSWORD environment variable is not set. Seeding skipped.")
        return

    db = SessionLocal()
    try:
        # Check if an admin user already exists
        existing_admin = db.query(User).filter(User.is_admin == True).first()
        if existing_admin:
            print(f"Database seeding: Admin user already exists ({existing_admin.email}). Skipping.")
            return

        # Check if a user with the admin email exists
        existing_user = db.query(User).filter(User.email == admin_email).first()
        if existing_user:
            # Promote existing user to admin
            existing_user.is_admin = True
            db.commit()
            print(f"Database seeding: Promoted existing user {admin_email} to admin successfully.")
        else:
            # Create new admin user
            hashed_pwd = hash_password(admin_password)
            new_admin = User(
                email=admin_email,
                hashed_password=hashed_pwd,
                is_admin=True
            )
            db.add(new_admin)
            db.commit()
            print(f"Database seeding: Admin user created successfully ({admin_email}).")
    except Exception as e:
        print(f"Database seeding: Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin_user()
