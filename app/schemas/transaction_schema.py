from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

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

    model_config = {
        "json_schema_extra": {
            "example": {
                "amount": 1000,
                "pin": 12345,
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

class CheckoutSessionResponse(BaseModel):
    session_id: Optional[str] = None
    session_url: Optional[str] = None
    clientSecret: Optional[str] = None

    class Config:
        from_attributes = False
        json_schema_extra = {
            "example": {
                "session_id": "1234567890",
                "session_url": "https://example.com/checkout/1234567890",
                "clientSecret": "sk_test_1234567890"
            }
        }

class CreatePaymentCardRequest(BaseModel):
    last_four_digits: str
    card_type: str
    expiration_month: int
    expiration_year: int
    tms_token: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "last_four_digits": "1234",
                "card_type": "Visa",
                "expiration_month": 12,
                "expiration_year": 2023,
                "tms_token": "1234567890"
            }
        }

class PaymentCardsResponse(BaseModel):
    id: int
    owner_id: int
    last_four_digits: str
    card_type: str
    expiration_month: int
    expiration_year: int
    tms_token: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "owner_id": 1,
                "last_four_digits": "1234",
                "card_type": "Visa",
                "expiration_month": 12,
                "expiration_year": 2023,
                "tms_token": "1234567890",
                "created_at": "2023-10-10T10:00:00",
                "updated_at": "2023-10-10T10:00:00"
            }
        }
