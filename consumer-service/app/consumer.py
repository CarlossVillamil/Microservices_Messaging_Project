import json
import time
import logging
import pika
from .config import RABBITMQ_URL, EXCHANGE_NAME, ROUTING_KEY, QUEUE_NAME

logging.getLogger("pika").setLevel(logging.CRITICAL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.consumer")


def connect_rabbitmq():
    while True:
        try:
            logger.info("Conectando a RabbitMQ...")
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            logger.info("Conectado a RabbitMQ")
            return connection

        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ no está disponible. Reintentando en 3 segundos...")
            time.sleep(3)


def start_consumer():
    logger.info("Starting consumer worker")

    connection = connect_rabbitmq()

    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(queue=QUEUE_NAME, exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY)

    logger.info(
        f"Consumer ready. Listening on queue '{QUEUE_NAME}' "
        f"(exchange='{EXCHANGE_NAME}', routing_key='{ROUTING_KEY}')"
    )

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body)
            logger.info(
                f"Message received | exchange={method.exchange}, "
                f"routing_key={method.routing_key}, tag={method.delivery_tag}"
            )
            logger.info(f"Message content: {message}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Message acknowledged")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    # Consumir
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
        channel.stop_consuming()
    finally:
        connection.close()
