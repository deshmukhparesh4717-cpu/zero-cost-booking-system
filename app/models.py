from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Booking(BaseModel):
    id: Optional[int] = None
    name: str
    phone: str
    date: str
    status: str = "pending"
    amount: float
    transaction_id: Optional[str] = None
    created_at: datetime = datetime.now()

class SMSPayload(BaseModel):
    sender: str
    content: str
    timestamp: Optional[str] = None