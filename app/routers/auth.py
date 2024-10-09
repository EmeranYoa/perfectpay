from enum import Enum

from fastapi import Depends, HTTPException, APIRouter, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, or_

from app.configs.config import settings
from app.configs.database import get_db
from app.core.oauth import create_access_token, get_current_user, create_refresh_token, refresh_token, role_required
from app.core.send_sms import sendsms
from app.core.utils import generate_pin_code, secure_pwd, verify_pwd, generate_merchant_code
from app.models.roles_model import Merchant
from app.models.session_model import Session
from app.models.user_model import User, create_user, create_user_partner, create_merchant_user
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin, UserLoginResponse, MerchantCreate

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)


class UserRole(str, Enum):
    client = "client"
    partner = "partner"
    merchant = "merchant"


@router.post("/register/partner", response_model=UserResponse)
async def register_partner(user: UserCreate, db: Session = Depends(get_db)):
    # check if user exists with the same phone number or email
    existing_user = db.query(User).filter(or_(User.phone_number == user.phone_number, User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number or email already registered")

    partner_code = generate_merchant_code()

    if not user.pin:
        user.pin = generate_pin_code()

    pin = user.pin
    user.pin = secure_pwd(pin)

    if user.password:
        user.password = secure_pwd(user.password)

    new_user = create_user_partner(db, user, secure_pwd(partner_code))

    # Envoyer un msg de bienvenue avec le code PIN par SMS
    response = sendsms(user.phone_number,
                       f"Bienvenue sur {settings.PROJECT_NAME}! Votre code PIN est : {pin}\nVotre code partenaire est : {partner_code}")
    if not response:
        raise HTTPException(status_code=500, detail="Failed to send SMS")

    return new_user


@router.post("/register/client", response_model=UserResponse)
async def register_client(user: UserCreate, db: Session = Depends(get_db),
                          partner=Depends(role_required(['partner', 'admin']))):
    # check if user exists
    existing_user = db.query(User).filter(or_(User.phone_number == user.phone_number, User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number or email already registered")

    if not user.pin:
        user.pin = generate_pin_code()

    pin = user.pin
    user.pin = secure_pwd(pin)

    if user.password:
        user.password = secure_pwd(user.password)

    new_user = create_user(db, user, partner.id)

    # Envoyer un msg de bienvenue avec le code PIN par SMS
    response = sendsms(user.phone_number, f"Bienvenue sur {settings.PROJECT_NAME}! Votre code PIN est : {pin}")
    if not response:
        raise HTTPException(status_code=500, detail="Failed to send SMS")

    return new_user


@router.post('/register/merchant', response_model=UserResponse)
async def register_merchant(user: MerchantCreate, db: Session = Depends(get_db),
                            partner=Depends(role_required(['partner', 'admin']))):
    # check if user exists
    existing_user = db.query(User).filter(or_(User.phone_number == user.phone_number, User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number or email  already registered")

    # check if business name exists
    existing_merchant = db.query(Merchant).filter(Merchant.business_name == user.business_name).first()
    if existing_merchant:
        raise HTTPException(status_code=400, detail="Business name already registered")

    merchant_code = generate_merchant_code()

    if not user.pin:
        user.pin = generate_pin_code()

    pin = user.pin
    user.pin = secure_pwd(pin)

    if user.password:
        user.password = secure_pwd(user.password)

    new_user = create_merchant_user(db, user, merchant_code, partner.id)

    # send welcome SMS with merchant code
    response = sendsms(user.phone_number,
                       f"Bienvenue sur {settings.PROJECT_NAME}! Votre code PIN est : {pin} et votre code marchand est : {merchant_code}")
    if not response:
        raise HTTPException(status_code=500, detail="Failed to send SMS")

    return new_user


@router.post("/login", response_model=UserLoginResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        or_(User.phone_number == user.phone_number, User.email == user.phone_number)).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.password and not user.pin:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Check if the provided pin or password is valid
    if user.pin and verify_pwd(user.pin, db_user.pin) == False:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if user.password and verify_pwd(user.password, db_user.password) == False:
        raise HTTPException(status_code=400, detail="Invalid password")

    # Génération des tokens JWT
    access_token = create_access_token({'sub': user.phone_number})
    r_token = create_refresh_token({'sub': user.phone_number})
    return {
        "access_token": access_token,
        "refresh_token": r_token,
        "token_type": "bearer",
        "user": db_user
    }


@router.post("/refresh_token")
def refresh_token(r_token: str = Depends(refresh_token)):
    return {"access_token": r_token}


@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=Page[UserResponse])
def get_users(
        db: Session = Depends(get_db),
        role: UserRole = Query(None, description="Filter user by role  (client, partner, merchant, admin)"),
        name: str = Query(None, description="Filter user by name"),
        phone_number: str = Query(None, description="Filter user by phone number"),
        user: User = Depends(role_required(['partner', 'admin']))):
    """
    Get all users filtered by role, name, and phone number. based on the current user role.
    """
    query = select(User).filter(user.phone_number != User.phone_number)

    if user.partner:
        query = query.filter(
            or_(
                User.merchant.registered_by == user.id,
                User.client.registered_by == user.id
            )
        )

    if role:
        if role == "partner" and user.admin:
            query = query.filter(User.partner)
        elif role == "client" and (user.admin or user.partner):
            query = query.filter(User.client)
        elif role == "merchant" and (user.admin or user.partner):
            query = query.filter(User.merchant)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: Insufficient role"
            )

    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))

    if phone_number:
        query = query.filter(User.phone_number.ilike(f"%{phone_number}%"))

    return paginate(db, query.order_by(User.updated_at.desc()))
