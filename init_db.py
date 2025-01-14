# init_db.py
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, MLModel, UserRole
from database import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Создаем демо пользователя и администратора
demo_user = User(user_id=str(uuid4()), username="demo_user", password="password", role=UserRole.USER, balance=100.0)
demo_admin = User(user_id=str(uuid4()), username="demo_admin", password="admin", role=UserRole.ADMIN)

# Создаем базовую ML модель
ml_model_1 = MLModel(model_id=str(uuid4()), name="Sample Model 1", description="A simple demo model", cost_per_request=10.0)
ml_model_2 = MLModel(model_id=str(uuid4()), name="Sample Model 2", description="Another demo model", cost_per_request=20.0)

db.add_all([demo_user, demo_admin, ml_model_1, ml_model_2])
db.commit()

print("Database initialized with demo users and ML models.")