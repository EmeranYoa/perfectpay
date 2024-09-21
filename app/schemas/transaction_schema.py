from pydantic import BaseModel
from datetime import datetime
from enum import Enum

# Schéma pour les transferts
class TransferRequest(BaseModel):
    recipient_phone: str
    amount: float
    pin: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "recipient_phone": "237691882411",
                "amount": 1000,
                "pin": 12345
            }
        }
    }

class WithdrawRequest(BaseModel):
    amount: float
    pin: int
    merchant_code: str
    merchan_phone: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 1000,
                "pin": 12345,
                "merchant_code": "123456",
                "merchan_phone": "237691882411"
            }
        }
    }

class Operator(str, Enum):
    ORANGE = "ORANGE"
    MTN = "MTN"

# Schéma pour la recharge
class RechargeRequest(BaseModel):
    amount: float
    operator: Operator
    pin: int

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 1000,
                "operator": "ORANGE",
                "pin": 12345
            }
        }
    }

class RechareCardRequest(BaseModel):
    amount: float
    pin: int
    card_number: str
    card_expiry: str
    card_cvv: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 1000,
                "pin": 12345,
                "card_number": "1234567890123456",
                "card_expiry": "12/25",
                "card_cvv": "123"
            }
        }
    }
# Schéma pour un paiement
class PaymentRequest(BaseModel):
    merchant_code: str
    amount: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "merchant_code": "123456",
                "amount": 1000
            }
        }

class TransactionResponse(BaseModel):
    id: int
    amount: float
    fees: float
    status: str
    user_id: int
    transaction_type: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "amount": 1000,
                "fees": 10,
                "status": "success",
                "user_id": 1,
                "transaction_type": "transfer",
                "created_at": "2023-10-10T10:00:00"
            }
        }

        
class TariffResponse(BaseModel):
    transaction_type: str
    min_amount: float
    max_amount: float
    fee: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "transaction_type": "transfer",
                "min_amount": 100,
                "max_amount": 1000,
                "fee": 10
            }
        }