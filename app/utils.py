import qrcode
import io
import base64
import requests
import pytesseract
from PIL import Image
import re

def generate_upi_qr(vpa: str, name: str, amount: float, booking_id: str):
    upi_link = f"upi://pay?pa={vpa}&pn={name}&am={amount}&tn=Booking_{booking_id}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(upi_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def send_whatsapp_message(api_url: str, api_key: str, phone: str, text: str, image_bytes: bytes = None):
    headers = {"apikey": api_key, "Content-Type": "application/json"}
    if image_bytes:
        payload = {
            "number": phone,
            "options": {"delay": 1200, "presence": "composing"},
            "mediaMessage": {
                "mediatype": "image",
                "caption": text,
                "media": base64.b64encode(image_bytes).decode('utf-8')
            }
        }
        endpoint = f"{api_url}/message/sendMedia/YOUR_INSTANCE_NAME"
    else:
        payload = {"number": phone, "text": text}
        endpoint = f"{api_url}/message/sendText/YOUR_INSTANCE_NAME"
    response = requests.post(endpoint, json=payload, headers=headers)
    return response.json()

def perform_ocr(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image)

def extract_upi_details(text: str):
    """
    Refined regex for major Indian UPI apps: PhonePe, GPay, Paytm.
    """
    # Amount: Matches ₹500, Rs 500, 500.00, etc.
    amount_match = re.search(r'(?:₹|Rs\.?|INR)\s*(\d+(?:\.\d{1,2})?)', text, re.IGNORECASE)
    
    # Transaction IDs / Reference Numbers
    # UPI Ref No / UTR is usually 12 digits
    # PhonePe: often starts with T followed by digits
    # GPay: Google Transaction ID
    txn_patterns = [
        r'(?:UPI\s*Ref\s*No|UTR|Ref\s*No)\s*[:\s]*(\d{12})',  # Standard UTR
        r'(?:Txn\s*ID|Transaction\s*ID)\s*[:\s]*([A-Z0-9]+)', # Generic Alpha-numeric
        r'(?:Google\s*Transaction\s*ID)\s*[:\s]*([A-Z0-9\._]+)', # GPay specific
    ]
    
    txn_id = None
    for pattern in txn_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            txn_id = match.group(1)
            break
            
    return {
        "amount": float(amount_match.group(1)) if amount_match else None,
        "txn_id": txn_id
    }
