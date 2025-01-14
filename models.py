# models.py
from datetime import datetime
from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Enum as SqlEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    _password = Column(String, nullable=False)  # Store the hashed password
    role = Column(SqlEnum(UserRole), nullable=False)
    balance = Column(Float, default=0.0)
    transactions = relationship("Transaction", back_populates="user") # Связь с таблицей транзакций
    ml_tasks = relationship("MLTask", back_populates="user") # Связь с таблицей задач

    def __init__(self, user_id, username, password, role=UserRole.USER, balance=0.0):
        self.user_id = user_id  # Идентификатор пользователя
        self.username = username
        self._password = password # Скрываем пароль
        self.role = role
        self.balance = balance

    def verify_password(self, password):
        return self._password == password # Проверка пароля

    def deposit(self, amount):
        if amount > 0:
           self.balance += amount
        else:
           raise ValueError("Сумма пополнения должна быть положительной")

    def withdraw(self, amount):
        if amount > 0 and self.balance >= amount:
           self.balance -= amount
        elif amount <=0 :
            raise ValueError("Сумма списания должна быть положительной")
        else:
            raise ValueError("Недостаточно средств на балансе")
        
    def __str__(self):
        return f"User(id={self.user_id}, username='{self.username}', role={self.role.value}, balance={self.balance})"
    

class MLModel(Base):
    __tablename__ = "ml_models"

    model_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    cost_per_request = Column(Float, nullable=False)
    
    ml_tasks = relationship("MLTask", back_populates="model") # Связь с таблицей задач

    def __init__(self, model_id, name, description, cost_per_request):
        self.model_id = model_id
        self.name = name
        self.description = description
        self.cost_per_request = cost_per_request

class MLTaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    
class MLTask(Base):
    __tablename__ = "ml_tasks"

    task_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    model_id = Column(String, ForeignKey("ml_models.model_id"), nullable=False)
    data = Column(String) # Можно хранить JSON
    status = Column(SqlEnum(MLTaskStatus), default=MLTaskStatus.PENDING)
    result = Column(String) # Можно хранить JSON
    timestamp = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="ml_tasks") # Связь с таблицей пользователей
    model = relationship("MLModel", back_populates="ml_tasks")# Связь с таблицей моделей
    
    def __init__(self, task_id, user, model, data, status=MLTaskStatus.PENDING, result=None,  timestamp = datetime.now()):
        self.task_id = task_id
        self.user = user
        self.model = model
        self.data = data
        self.status = status
        self.result = result
        self.timestamp = timestamp

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    ML_REQUEST = "ml_request"

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    type = Column(SqlEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    task_id = Column(String, ForeignKey("ml_tasks.task_id"), nullable=True)
    
    user = relationship("User", back_populates="transactions") # Связь с таблицей пользователей
    

    def __init__(self, transaction_id, user, type, amount, timestamp=datetime.now(), task_id=None):
        self.transaction_id = transaction_id
        self.user = user
        self.type = type
        self.amount = amount
        self.timestamp = timestamp
        self.task_id = task_id # Идентификатор задачи, если это списание за ML запрос
