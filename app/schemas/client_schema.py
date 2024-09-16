from pydantic import BaseModel
from typing import Optional

class ClientBase(BaseModel):
    phone_number: str
    pin: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "237691882411",
                "pin": "123456",
            }
        }
    }
    
class ClientCreate(ClientBase):
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "237691882411",
                "pin": "123456",
            }
        }
    }
    
class ClientCreateResponseSchema(BaseModel):
    id: int
    phone_number: str
    pin: str
    balance: float
    type: str
    address: Optional[str] = None
    market_code: Optional[str] = None
    status: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "phone_number": "237691882411",
                "pin": "123456",
                "balance": 1000.0,
                "type": "client",
                "address": "123 Main St, City, Country",
                "market_code": "123456",
                "status": "active",
                "email": "john.doe@example.com"
            }
        }

class TransferRequest(BaseModel):
    from_phone: str
    to_phone: str
    amount: float
    pin: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "from_phone": "237691882411",
                "to_phone": "237691882412",
                "amount": 100.0,
                "pin": "123456"
            }
        }
    }

class TransferResponseSchema(BaseModel):
    message: str
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "message": "Transfer successful"
            }
        }

class SoldeRequest(BaseModel):
    phone_number: str
    pin: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "237691882411",
                "pin": "123456"
            }
        }
    }

class SoldeResponse(BaseModel):
    solde: float
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "solde": 1000.0
            }
        }

class RechargeRequest(BaseModel):
    phone_number: str
    amount: float
    pin: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "237691882411",
                "amount": 100.0,
                "pin": "123456"
            }
        }
    }

class RechargeResponse(BaseModel):
    message: str
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "message": "Recharge successful"
            }
        }
