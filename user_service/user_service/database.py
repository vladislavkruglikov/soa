import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_path = os.getenv("DATABASE_FILE_NAME", "sqlite:////app/users.db")
if db_path.startswith("sqlite:///"):
    file_path = db_path[10:]  # Remove "sqlite:///"
    Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)

engine = create_engine(
    db_path, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()