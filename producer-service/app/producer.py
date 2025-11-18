import pika
import json
import logging
from .config import RABBITMQ_URL, EXCHANGE_NAME, ROUTING_KEY

logger = logging.getLogger(__name__)

def get_connection():
    params = pika.URLParameters(RABBITMQ_URL)
    return pika.BlockingConnection(params)

def publish_message(message: dict):
    try:
        connection = get_connection()
        channel = connection.channel()

        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type="topic",
            durable=True
        )

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )

        logger.info("Message published successfully")
        connection.close()

    except Exception as e:
        logger.error(f"Error publishing message: {e}")
        raise
