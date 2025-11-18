import os

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://admin:admin@localhost:5672/"
)

QUEUE_NAME = "shipment_updates"
EXCHANGE_NAME = "logistics_exchange"
ROUTING_KEY = "shipment.update"
