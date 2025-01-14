# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "sqlite:///./ml_service.db" # Путь к БД

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # Создание движка
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Создание сессии


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    Base.metadata.create_all(engine)