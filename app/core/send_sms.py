import requests
from configs.config import settings

def sendsms(to: str, message: str) -> str:
    sender = settings.SMS_SENDER
    url = settings.SMS_ENDPOINT
    payload = {
        "api_key": settings.SMS_API_KEY,
        "password": settings.SMS_PASSWORD,
        "sender": sender,
        "message": message,
        "phone": to,
        "flag": "short_sms"
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}

    response = requests.post(url, data=payload, headers=headers)
    
    result = response.json()
    return result.get("status") == "success"