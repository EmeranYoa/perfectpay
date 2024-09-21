from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from configs.database import get_db
from models.merchant_model import Merchant, get_merchant
from models.user_model import User, create_user, get_user
from schemas.merchant_schema import MerchantCreate, MerchantResponse, MerchantUpdate
from core.utils import generate_merchant_code, generate_pin_code, secure_pwd, verify_pwd
from core.send_sms import sendsms
from core.oauth import get_current_user
from configs.config import settings

router = APIRouter(
    prefix="/api/v1/merchants",
    tags=["Merchants"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register", response_model=MerchantResponse)
async def register_merchant(merchant: MerchantCreate, db: Session = Depends(get_db)):
    # Vérifier si le marchand existe déjà
    existing_merchant_user  = get_user(db, merchant.owner.phone_number)
    if existing_merchant_user:
        raise HTTPException(status_code=400, detail="User phone number already registered")

    existing_merchant = db.query(Merchant).filter(Merchant.phone_number == merchant.phone_number).first()
    if existing_merchant:
        raise HTTPException(status_code=400, detail="Merchant phone number already registered")
    
    
    pin = generate_pin_code()
    merchant.owner.pin = secure_pwd(pin)

    owner = merchant.owner
    del merchant.owner

    # create new merchant
    code = generate_merchant_code()
    new_merchant = Merchant(**merchant.dict(), merchant_code=secure_pwd(code))

    # create new the merchant with the merchant id
    owner.merchant_id = new_merchant.id
    user = create_user(db, owner)

    
    db.add(new_merchant)
    db.commit()
    db.refresh(new_merchant)


    # send a welcome message to the merchant with the code PIN and merchant code
    response = sendsms(merchant.phone_number, f"Bienvenue sur {settings.PROJECT_NAME}! Votre code PIN est : {pin} et votre code marchand est : {code}")
    return new_merchant

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

@router.get("/", response_model=list[MerchantResponse])
def get_merchants(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    merchants = db.query(Merchant).all()
    return merchants

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