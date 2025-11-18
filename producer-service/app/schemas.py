from pydantic import BaseModel
from typing import Optional

class Location(BaseModel):
    lat: float
    lng: float

class ShipmentUpdate(BaseModel):
    shipmentId: str
    status: str
    timestamp: str
    location: Optional[Location]
