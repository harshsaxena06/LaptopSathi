"""Creates all database tables. Run once before the first ingestion."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db

if __name__ == "__main__":
    init_db()
    print("Database tables created.")
