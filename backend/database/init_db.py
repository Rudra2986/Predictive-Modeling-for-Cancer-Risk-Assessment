import os
import sys

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from backend.database.session import engine, Base
from backend.database.base import User, PredictionLog, ChatMessage

def init_database():
    print("Connecting to PostgreSQL database...")
    try:
        # Create all tables defined in Base
        Base.metadata.create_all(bind=engine)
        print("Success: Database tables initialized successfully!")
        print("Created tables: 'users', 'prediction_logs', 'chat_messages'")
    except Exception as e:
        print(f"Error: Failed to connect or initialize database: {e}")
        print("\nMake sure your PostgreSQL local setup is active and running.")
        print(f"Connection URL used: {engine.url.render_as_string(hide_password=True)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
