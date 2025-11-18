from .consumer import start_consumer
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info("Starting consumer worker")
    start_consumer()
