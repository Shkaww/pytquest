from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from models import User, MLModel, MLTask, Transaction, MLTaskStatus, TransactionType, UserRole
from exceptions import InsufficientFundsError, InvalidDataError, AuthenticationError

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username, password, role=UserRole.USER, balance=0.0):
        user_id = str(uuid4())
        user = User(user_id, username, password, role, balance)
        self.db.add(user)
        self.db.commit()
        return user

    def get_user_by_username(self, username):
        return self.db.query(User).filter(User.username == username).first()

    def authenticate_user(self, username, password):
        user = self.get_user_by_username(username)
        if not user or not user.verify_password(password):
            raise AuthenticationError("Invalid username or password")
        return user
    
    def get_user_by_id(self, user_id):
        return self.db.query(User).filter(User.user_id == user_id).first()

    def deposit(self, user, amount):
        user.deposit(amount)
        transaction_id = str(uuid4())
        transaction = Transaction(transaction_id, user, TransactionType.DEPOSIT, amount, datetime.now())
        self.db.add(transaction)
        self.db.commit()
        return user

    def withdraw(self, user, amount):
        user.withdraw(amount)
        transaction_id = str(uuid4())
        transaction = Transaction(transaction_id, user, TransactionType.WITHDRAWAL, amount, datetime.now())
        self.db.add(transaction)
        self.db.commit()
        return user

    def get_balance(self, user):
        return user.balance
    
class MLService:
    def __init__(self, db: Session, ml_queue=None):
        self.db = db
        self.ml_queue = ml_queue # Будет передан RabbitMQ

    def get_available_models(self):
        return self.db.query(MLModel).all()

    def get_model_by_id(self, model_id):
        return self.db.query(MLModel).filter(MLModel.model_id == model_id).first()

    def create_ml_task(self, user, model, data):
            task_id = str(uuid4())
            ml_task = MLTask(task_id, user, model, data)
            self.db.add(ml_task)
            self.db.commit()
            return ml_task

    def process_ml_task(self, task, validate_data_func, predict_func):
        
        model = task.model
        user = task.user
        data = task.data
       
        if user.balance < model.cost_per_request:
            task.status = MLTaskStatus.FAILED
            self.db.commit()
            raise InsufficientFundsError("Недостаточно средств для выполнения ML запроса")
        
        try:
            # Валидация данных
            valid_data, errors = validate_data_func(data)
            
            if errors:
                task.status = MLTaskStatus.FAILED
                task.result = {"errors":errors}
                self.db.commit()
                raise InvalidDataError(errors)
            
            task.status = MLTaskStatus.PROCESSING
            self.db.commit()
            result = predict_func(valid_data)
            task.result = result
            task.status = MLTaskStatus.COMPLETED

            user.withdraw(model.cost_per_request)
            transaction_id = str(uuid4())
            transaction = Transaction(transaction_id,user, TransactionType.ML_REQUEST,model.cost_per_request, datetime.now(), task.task_id)
            self.db.add(transaction)
            self.db.commit()
            
            return task
        except Exception as e:
                task.status = MLTaskStatus.FAILED
                task.result = {"error": str(e)}
                self.db.commit()
                raise e
    
    def get_ml_task_by_id(self, task_id):
        return self.db.query(MLTask).filter(MLTask.task_id == task_id).first()
            
class TransactionService:
    def __init__(self, db: Session):
         self.db = db

    def get_user_transactions(self, user):
         return self.db.query(Transaction).filter(Transaction.user == user).all()