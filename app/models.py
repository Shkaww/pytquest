from datetime import datetime

class User:
    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.balance = 0  # Conditional credits

    def add_balance(self, amount: int):
        self.balance += amount

    def deduct_balance(self, amount: int) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

class Transaction:
    def __init__(self, user_id: int, amount: int, type_: str, description: str):
        self.user_id = user_id
        self.amount = amount
        self.type_ = type_
        self.description = description
        self.timestamp = datetime.now()

class MLTask:
    def __init__(self, user_id: int, data: dict):
        self.user_id = user_id
        self.data = data
        self.status = "pending"  # pending, in_progress, completed, failed

class Prediction:
    def __init__(self, task_id: int, result: dict, cost: int):
        self.task_id = task_id
        self.result = result
        self.cost = cost