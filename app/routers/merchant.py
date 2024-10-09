from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.models.roles_model import Merchant, get_merchant
from app.models.user_model import User, create_user, get_user
from app.schemas.merchant_schema import MerchantCreate, MerchantResponse, MerchantUpdate
from app.core.utils import generate_merchant_code, generate_pin_code, secure_pwd, verify_pwd
from app.core.send_sms import sendsms
from app.core.oauth import get_current_user
from app.configs.config import settings

router = APIRouter(
    prefix="/api/v1/merchants",
    tags=["Merchants"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{phone_number}/{merchant_code}", response_model=MerchantResponse)
def get_merchant_by_code_and_phone_number(phone_number: str, merchant_code: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    merchant = get_merchant(db, phone_number)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    if not verify_pwd(merchant_code, merchant.merchant_code):
        raise HTTPException(status_code=404, detail="Marchant not found")
    return merchant

@router.get("/{phone_number}", response_model=MerchantResponse)
def get_merchant_by_phone_number(phone_number: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    merchant = get_merchant(db, phone_number)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant


@router.put("/{phone_number}/{merchant_code}", response_model=MerchantResponse)
def update_merchant(phone_number: str, merchant_code: str, merchant: MerchantUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    merchant_to_update = get_merchant(db, phone_number)
    
    if not merchant_to_update:
        raise HTTPException(status_code=404, detail="Merchant not found")

    if not verify_pwd(merchant_code, merchant_to_update.merchant_code):
        raise HTTPException(status_code=404, detail="Marchant not found")

    for key, value in merchant.dict().items():
        setattr(merchant_to_update, key, value)
    db.commit()
    db.refresh(merchant_to_update)
    return merchant_to_update