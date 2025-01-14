from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

def get_engine():
    return create_engine("sqlite:///personal_account.db", echo=True)

class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    balance = Column(Float, default=0)

class TransactionModel(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    type_ = Column(String, nullable=False)
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MLTaskModel(Base):
    __tablename__ = 'ml_tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    data = Column(JSON, nullable=False)
    status = Column(String, default='pending')

class PredictionModel(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('ml_tasks.id'), nullable=False)
    result = Column(JSON, nullable=False)
    cost = Column(Integer, nullable=False)

engine = get_engine()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)