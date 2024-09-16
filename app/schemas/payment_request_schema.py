from pydantic import BaseModel

class PaymentRequest(BaseModel):
    phone_number: str
    amount_to_charge: float
    SMSNotification: bool

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "237691882411",
                "amount_to_charge": 100.0,
                "SMSNotification": True
            }
        }
class PaymentResponse(BaseModel):
    message: str
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Payment successful",
                "status": "success"
            }
        }

