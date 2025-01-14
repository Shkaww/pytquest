# worker.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import time
from message_queue import MessageQueue
from services import  MLService
from database import get_db
from models import MLTaskStatus

def callback(ch, method, properties, body):
    message = json.loads(body)
    task_id = message.get("task_id")
    db = next(get_db())
    ml_service = MLService(db)
    ml_task = ml_service.get_ml_task_by_id(task_id)

    if not ml_task:
        print(f"Task with id {task_id} not found.")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    
    def validate_data(data):
            # Тут будет функция валидации
            return data, None
        
    def predict(data):
        # Тут будет функция предсказания
        time.sleep(2)
        return {"prediction": "test prediction"}
    
    try:
        ml_service.process_ml_task(ml_task, validate_data, predict)
        print(f"Task {task_id} completed")
    except Exception as e:
         ml_task.status = MLTaskStatus.FAILED
         ml_task.result = str(e)
         db.commit()
         print(f"Task {task_id} failed: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    queue = MessageQueue()
    queue.connect()
    queue.consume(callback)
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)