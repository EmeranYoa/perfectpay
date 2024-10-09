import uuid
import requests
from app.configs.config import settings

def paycool(amount: float, client_phone: str, customer_name = settings.PROJECT_NAME) -> dict:
    url = settings.PAYCOOL_ENPOINT

    payload = {
        "transaction_amount": amount,
        "transaction_currency": "XAF",
        "transaction_reason": "Recharge de compte",
        "app_transaction_ref": str(uuid.uuid4()),
        "customer_phone_number": client_phone,
        "customer_name": customer_name,
        "customer_email": settings.PAYCOOL_EMAIL,
        "customer_lang": "fr"
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(url, data=payload, headers=headers)
    return response.json()