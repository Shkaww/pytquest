# test_database.py
from database import create_database, get_db
from services import UserService, MLService, TransactionService
from uuid import uuid4

def test_database():
    create_database()  # Создаем таблицы, если их нет
    db = next(get_db())
    user_service = UserService(db)
    ml_service = MLService(db)
    transaction_service = TransactionService(db)

    # Создание пользователя
    new_user = user_service.create_user("test_user", "test_password")
    assert new_user.username == "test_user"

    # Пополнение баланса
    user_service.deposit(new_user, 50)
    assert user_service.get_balance(new_user) == 50

    # Списание с баланса
    user_service.withdraw(new_user, 20)
    assert user_service.get_balance(new_user) == 30
   
    # Аутентификация пользователя
    auth_user = user_service.authenticate_user("test_user", "test_password")
    assert auth_user.username == "test_user"

    # Получение пользователя по ID
    get_user = user_service.get_user_by_id(auth_user.user_id)
    assert auth_user.username == get_user.username
    
    # Получение списка моделей
    available_models = ml_service.get_available_models()
    assert len(available_models) > 0
    
    # Получение модели по ID
    model_id = available_models[0].model_id
    get_model = ml_service.get_model_by_id(model_id)
    assert get_model.model_id == model_id
    
    # Создание ML задачи
    test_model = available_models[0]
    ml_task = ml_service.create_ml_task(new_user, test_model, "test_data")
    assert ml_task.user.username == "test_user"
    
    # Получение истории транзакций
    transactions = transaction_service.get_user_transactions(new_user)
    assert len(transactions) > 0
    
    print("Database tests passed!")

if __name__ == "__main__":
    test_database()