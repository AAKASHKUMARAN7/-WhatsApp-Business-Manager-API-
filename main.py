!pip install fastapi[all] python-dotenv requests



from fastapi import FastAPI, Query, HTTPException
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FastAPI app instance
app = FastAPI(title="TMBC WhatsApp Sender", version="1.1")

# Load WhatsApp credentials from .env
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")

# Phone number validation
def is_valid_phone_number(phone: str) -> bool:
    return phone.startswith("+") and phone[1:].isdigit() and 10 <= len(phone[1:]) <= 15

#  Helper to send message using WhatsApp API
def send_whatsapp_message(phone_number: str, message_body: str):
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message_body
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return {
            "status": "success",
            "message": f"Message sent to {phone_number}",
            "whatsapp_response": response.json()
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

#  Original endpoint with fixed message
@app.get("/send_message")
def send_message(phone_number: str = Query(..., description="Phone number in E.164 format, e.g., +14155552671")):
    if not is_valid_phone_number(phone_number):
        raise HTTPException(status_code=400, detail="Invalid phone number format.")
    
    fixed_message = "Hello, this is a test message from our TMBC bot!"
    return send_whatsapp_message(phone_number, fixed_message)

#  New endpoint with custom message support
@app.get("/send_custom_message")
def send_custom_message(
    phone_number: str = Query(..., description="Phone number in E.164 format"),
    message: str = Query(..., description="Message to send")
):
    if not is_valid_phone_number(phone_number):
        raise HTTPException(status_code=400, detail="Invalid phone number format.")
    
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    return send_whatsapp_message(phone_number, message.strip())


