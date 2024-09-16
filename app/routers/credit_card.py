from fastapi import APIRouter, Depends, HTTPException
from schemas.credit_card_payment_request_schema import CreditCardPaymentRequest
from schemas.payment_request_schema import PaymentResponse
from sqlalchemy.orm import Session
from configs.database import get_db
from models.client_model import Client, get_client
from core.paycool import paycool
from core.send_sms import sendsms

router = APIRouter(
    prefix="/api/v1/payin-credit-card",
    tags=["payment-channel"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=PaymentResponse)
def credit_card_channel(request: CreditCardPaymentRequest, db: Session = Depends(get_db)):
    marchant = get_client(db, request.phone_number)

    if not marchant:
        raise HTTPException(status_code=404, detail="Client not found")
    
    result ={
        "success": True,
        "message": "Payment method comming soon",
    }
    
    return HTTPException(status_code=400, detail="Payment failed")