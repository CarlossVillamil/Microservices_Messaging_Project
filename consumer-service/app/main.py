from fastapi import FastAPI
import threading
from .consumer import start_consumer

app = FastAPI()

@app.on_event("startup")
def launch_consumer():
    """Runs RabbitMQ consumer in a background thread."""
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()
    print(" Consumer thread started!")

@app.get("/")
def root():
    return {"status": "consumer running"}