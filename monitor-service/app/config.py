import os

RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://admin:admin@rabbit:5672/"
)

PRODUCER_URL = os.getenv("PRODUCER_URL", "http://producer:8001")
QUEUE_NAME = os.getenv("QUEUE_NAME", "shipment_updates")
