import uuid
import requests
from configs.config import settings

def paycool(amount: float, client_phone: str) -> dict:
    url = settings.PAYCOOL_ENPOINT

    payload = {
        "transaction_amount": amount,
        "transaction_currency": "XAF",
        "transaction_reason": "Recharge de compte",
        "app_transaction_ref": str(uuid.uuid4()),
        "customer_phone_number": client_phone,
        "customer_name": client_phone,
        "customer_email": settings.PAYCOOL_EMAIL,
        "customer_lang": "fr"
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()