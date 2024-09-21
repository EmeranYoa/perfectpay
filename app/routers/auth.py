import random
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from configs.database import get_db
from configs.config import settings
from core.send_sms import sendsms
from core.paycool import paycool
from schemas.user_schema  import UserCreate, UserResponse, UserLogin, UserLoginResponse
from models.user_model import User, create_user
from models.api_key_model import APIKey
from models.merchant_model import Merchant
from models.session_model import Session
from models.tarif_model import Tariff
from models.transaction_model import Transaction
from core.utils import generate_pin_code, secure_pwd, verify_pwd
from core.oauth import create_access_token, get_current_user, create_refresh_token, refresh_token

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.phone_number == user.phone_number).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    pin = generate_pin_code()
    
    user.pin = secure_pwd(pin)

    if user.password:
        user.password = secure_pwd(user.password)
    
    new_user = create_user(db, user)

    # Envoyer un msg de bienvenue avec le code PIN par SMS
    response = sendsms(user.phone_number, f"Bienvenue sur {settings.PROJECT_NAME}! Votre code PIN est : {pin}")
    if response == False:
        raise HTTPException(status_code=500, detail="Failed to send SMS")
    
    return  new_user

@router.post("/login", response_model=UserLoginResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone_number == user.phone_number).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.password and not user.pin:
        raise HTTPException(status_code=400, detail="Invalid credentials")
        
    # Check if the provided pin or password is valid
    if user.pin and verify_pwd(user.pin, db_user.pin) == False:
        raise HTTPException(status_code=400, detail="Invalid PIN")
    
    if user.password and verify_pwd(user.password, db_user.password) == False:
        raise HTTPException(status_code=400, detail="Invalid password")
    
    # Génération des tokens JWT
    access_token = create_access_token({'sub': user.phone_number})
    refresh_token = create_refresh_token({'sub': user.phone_number})
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.post("/refresh_token")
def refresh_token(refresh_token: str = Depends(refresh_token)):
    return {"access_token": refresh_token}

@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user
