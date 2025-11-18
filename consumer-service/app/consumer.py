import pika
import json
import time
from .config import RABBITMQ_URL, QUEUE_NAME, EXCHANGE_NAME, ROUTING_KEY

def start_consumer():

    while True:  # <-- Loop para reconectar si se cae
        try:
            print("Trying to connect to RabbitMQ...",flush=True)
            
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            # Declare exchange and queue
            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type="topic",
                durable=True
            )

            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            channel.queue_bind(
                queue=QUEUE_NAME,
                exchange=EXCHANGE_NAME,
                routing_key=ROUTING_KEY
            )

            print("Consumer READY — listening for messages...",flush=True)

            # Callback
            def callback(ch, method, properties, body):
                message = json.loads(body)
                print("📦 Received shipment update:", message)
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=callback,
                auto_ack=False  # good practice
            )

            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ not ready, retrying in 3s...",flush=True)
            time.sleep(3)
        except Exception as e:
            print("Consumer error:", str(e),)
            time.sleep(3)