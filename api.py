# api.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db, create_database
from services import UserService, MLService, TransactionService
from models import UserRole, MLTaskStatus, MLModel, MLTask, Transaction, User
from exceptions import InsufficientFundsError, InvalidDataError, AuthenticationError
from message_queue import MessageQueue

app = FastAPI()
create_database()

# Инициализируем MessageQueue
message_queue = MessageQueue()

# --- Pydantic Models ---
class UserCreate(BaseModel):
    username: str = Field(..., description="Username for registration")
    password: str = Field(..., description="Password for registration")

class UserLogin(BaseModel):
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")

class BalanceDeposit(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to deposit, must be positive")

class MLRequest(BaseModel):
    model_id: str = Field(..., description="ID of the ML model to use")
    data: str = Field(..., description="Input data for ML model in JSON string format")

class TransactionResponse(BaseModel):
    transaction_id: str
    type: str
    amount: float
    timestamp: str
    task_id: Optional[str] = None

class MLTaskResponse(BaseModel):
    task_id: str
    model_name: str
    data: str = Field(..., description="Input data for ML model in JSON string format")
    status: str
    result: Optional[str]
    timestamp: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    role: str
    balance: float
    
class MLModelResponse(BaseModel):
    model_id: str
    name: str
    description: Optional[str] = None
    cost_per_request: float


# --- Dependency Injection ---
def get_current_user(db: Session = Depends(get_db), username: str = None, password: str = None) -> User:
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    user_service = UserService(db)
    try:
        user = user_service.authenticate_user(username, password)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        )
    return user

def get_ml_service(db: Session = Depends(get_db)):
    return MLService(db, ml_queue=message_queue)

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)

def get_transaction_service(db: Session = Depends(get_db)):
    return TransactionService(db)


# --- Endpoints ---
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    try:
        user = user_service.create_user(user_data.username, user_data.password)
        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            role=user.role.value,
            balance=user.balance,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@app.post("/auth/login", response_model=UserResponse)
def login_user(user_data: UserLogin, user_service: UserService = Depends(get_user_service)):
    try:
        user = user_service.authenticate_user(user_data.username, user_data.password)
        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            role=user.role.value,
            balance=user.balance,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        )


@app.get("/users/balance", response_model=float)
def get_user_balance(current_user: User = Depends(get_current_user), user_service: UserService = Depends(get_user_service)):
    return user_service.get_balance(current_user)


@app.post("/users/deposit", response_model=UserResponse)
def deposit_user_balance(
    deposit_data: BalanceDeposit,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = user_service.deposit(current_user, deposit_data.amount)
        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            role=user.role.value,
            balance=user.balance,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@app.get("/ml/models", response_model=List[MLModelResponse])
def get_available_models(ml_service: MLService = Depends(get_ml_service)):
    models = ml_service.get_available_models()
    return [
        MLModelResponse(
           model_id=model.model_id,
            name=model.name,
            description=model.description,
            cost_per_request=model.cost_per_request
        )
        for model in models
    ]


@app.post("/ml/predict", response_model=MLTaskResponse)
def make_ml_prediction(
    request_data: MLRequest,
    current_user: User = Depends(get_current_user),
    ml_service: MLService = Depends(get_ml_service),
):
    try:
        model = ml_service.get_model_by_id(request_data.model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
            )

        ml_task = ml_service.create_ml_task(current_user, model, request_data.data)
        message_queue.publish({"task_id": ml_task.task_id})

        return MLTaskResponse(
            task_id=ml_task.task_id,
            model_name=ml_task.model.name,
            data=ml_task.data,
            status=ml_task.status.value,
            result=str(ml_task.result) if ml_task.result else None,
            timestamp=str(ml_task.timestamp),
        )
    except InsufficientFundsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except InvalidDataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@app.get("/transactions", response_model=List[TransactionResponse])
def get_user_transactions(
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    transactions = transaction_service.get_user_transactions(current_user)
    return [
        TransactionResponse(
            transaction_id=t.transaction_id,
            type=t.type.value,
            amount=t.amount,
            timestamp=str(t.timestamp),
            task_id=t.task_id,
        )
        for t in transactions
    ]