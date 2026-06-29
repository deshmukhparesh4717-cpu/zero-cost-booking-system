from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from .models import Booking, SMSPayload
from .utils import generate_upi_qr, send_whatsapp_message, perform_ocr, extract_upi_details
from .database import engine, Base, BookingModel, get_db
import os
import re

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuration
VPA = os.getenv("UPI_VPA", "yourname@upi")
MERCHANT_NAME = os.getenv("MERCHANT_NAME", "Your Business")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")

@app.post("/voice-receive")
async def voice_receive(payload: dict, db: Session = Depends(get_db)):
    text = payload.get("text", "").lower()
    phone = payload.get("phone", "919876543210")
    
    if any(keyword in text for keyword in ["book", "appointment", "reserve"]):
        amount = 500.0
        
        # Create DB record
        new_booking = BookingModel(
            phone=phone,
            transcript=text,
            amount=amount,
            status='pending',
            booking_date_info="Extracted from voice"
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        
        qr_bytes = generate_upi_qr(VPA, MERCHANT_NAME, amount, str(new_booking.id))
        
        msg = (f"Hi! We heard your booking request: \"{text}\".\n\n"
               f"To confirm, please pay ₹{amount} via this QR. "
               "Once done, reply with a screenshot of the receipt here.")
               
        send_whatsapp_message(EVOLUTION_API_URL, EVOLUTION_API_KEY, phone, msg, qr_bytes)
        
        return {"status": "success", "booking_id": str(new_booking.id)}
    
    return {"status": "ignored", "reason": "No booking intent detected"}

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    msg_data = data.get("data", {})
    message_type = msg_data.get("messageType")
    
    if message_type == "imageMessage":
        remote_jid = msg_data.get("key", {}).get("remoteJid", "")
        phone = remote_jid.split("@")[0]
        msg_id = msg_data.get("key", {}).get("id")
        background_tasks.add_task(process_receipt, phone, msg_id)
        
    return {"status": "received"}

async def process_receipt(phone: str, msg_id: str):
    # Dependency Injection doesn't work directly in background tasks, so we create a session manually
    from .database import SessionLocal
    db = SessionLocal()
    try:
        # 1. Download media (Placeholder)
        # image_bytes = requests.get(f"{EVOLUTION_API_URL}/message/downloadMedia/{msg_id}", headers=...).content
        image_bytes = b"" 
        if not image_bytes: return

        # 2. OCR and Extraction
        extracted_text = perform_ocr(image_bytes)
        details = extract_upi_details(extracted_text)
        
        if details['txn_id']:
            # 3. Find the most recent pending booking for this phone number
            booking = db.query(BookingModel).filter(
                BookingModel.phone == phone,
                BookingModel.status == 'pending'
            ).order_by(BookingModel.created_at.desc()).first()
            
            if booking:
                booking.status = 'confirmed'
                booking.upi_txn_id = details['txn_id']
                booking.receipt_ocr_text = extracted_text
                db.commit()
                
                confirmation_msg = f"✅ Payment Verified!\nTxn ID: {details['txn_id']}\nAmount: ₹{details['amount']}\n\nYour booking is CONFIRMED."
                send_whatsapp_message(EVOLUTION_API_URL, EVOLUTION_API_KEY, phone, confirmation_msg)
            else:
                send_whatsapp_message(EVOLUTION_API_URL, EVOLUTION_API_KEY, phone, "We found a payment but no pending booking. An agent will check this shortly.")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)