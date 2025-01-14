# message_queue.py

import pika
import json

class MessageQueue:
    def __init__(self, host='localhost', queue_name='ml_tasks'):
        self.host = host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def publish(self, message):
        if self.channel is None:
            self.connect()
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2) # make message persistent
        )

    def consume(self, callback):
        if self.channel is None:
            self.connect()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
        self.channel.start_consuming()

    def close(self):
        if self.connection is not None:
            self.connection.close()