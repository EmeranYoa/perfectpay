from fastapi import APIRouter, Depends, HTTPException
from schemas.payment_request_schema import PaymentRequest, PaymentResponse
from sqlalchemy.orm import Session
from configs.database import get_db
from models.client_model import Client, get_client, increase_client_balance
from core.paycool import paycool
from core.send_sms import sendsms

router = APIRouter(
    prefix="/api/v1/payin-ussd",
    tags=["payment-channel"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=PaymentResponse)
def ussd_channel(request: PaymentRequest, db: Session = Depends(get_db)):
    client = get_client(db, request.phone_number)

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    result = paycool(request.amount_to_charge, request.phone_number)
    
    if result:
        increase_client_balance(db, request.phone_number, request.amount_to_charge)
        return {
            "message": "Payment successful",
            "status": "success"
        }
    
    return HTTPException(status_code=400, detail={"message": "Payment failed", "status": "failed"})