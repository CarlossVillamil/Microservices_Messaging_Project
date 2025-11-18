from fastapi import FastAPI
from .producer import publish_message
from .schemas import ShipmentUpdate

app = FastAPI()

@app.get("/")
def root():
    return {"service": "Producer", "status": "Running"}

@app.post("/send-shipment")
def send_shipment(update: ShipmentUpdate):
    publish_message(update.dict())
    return {"message": "Shipment update sent!"}


