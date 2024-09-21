from sqlalchemy.orm import Session
from configs.database import get_db
from models.user_model import User, get_user
from schemas.transaction_schema import RechargeRequest, Operator, TransactionResponse, RechareCardRequest
from models.merchant_model import Merchant, get_merchant
from models.transaction_model import Transaction
from fastapi import APIRouter, Depends, HTTPException, status
from core.send_sms import sendsms
from core.utils import verify_pwd
from core.oauth import get_current_user
from core.paycool import paycool

router = APIRouter(
    prefix="/api/v1/recharges",
    tags=["Recharges"],
    responses={404: {"description": "Not found"}},
)

@router.post("/mobile-money", response_model=TransactionResponse)
async def recharge_using_mobile_money(data: RechargeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if PIN is correct
    if not verify_pwd(str(data.pin), user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")

    # Verify operator is supported
    if data.operator not in [Operator.ORANGE, Operator.MTN]:
        raise HTTPException(status_code=400, detail="Unsupported operator")

    try:
        # response = paycool(data.amount, user.phone_number)
        # if response["status"] != "success":
        #     raise HTTPException(status_code=400, detail="Payment failed")
        
        # Create credit transaction
        credit_transaction = Transaction(
            amount=data.amount,
            user_id=user.id,
            transaction_type="credit",
            status="completed"
        )
        db.add(credit_transaction)
        
        # Update user balance
        user.wallet.balance += data.amount
        db.commit()  # Commit changes
        db.refresh(user.wallet)  # Refresh wallet after update
        db.refresh(credit_transaction)

        # Send SMS notification
        sendsms(
            user.phone_number,
            f"Vous avez rechargé votre compte de {data.amount} FCFA. Votre nouveau solde est de {user.wallet.balance} FCFA."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Transaction failed")

    return credit_transaction

@router.post("/card", response_model=TransactionResponse)
async def recharge_using_card(data: RechareCardRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if PIN is correct
    if not verify_pwd(str(data.pin), user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")
    
    return {"message": "Recharge using card comming soon"}