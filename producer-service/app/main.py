from fastapi import FastAPI
from .producer import publish_message
from .schemas import ShipmentUpdate
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def root():
    return {"service": "Producer", "status": "Running"}

@app.post("/send-shipment")
def send_shipment(update: ShipmentUpdate):
    message_dict = update.dict()
    logger.info("Received shipment update request")
    
    publish_message(message_dict)

    return {
        "message": "Shipment update sent",
        "data": message_dict
    }
