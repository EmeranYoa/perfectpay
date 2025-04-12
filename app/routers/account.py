from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.core.oauth import get_current_user
from app.core.send_sms import sendsms
from app.core.utils import verify_pwd, secure_pwd
from app.models.user_model import User
from app.schemas.user_schema import UserBalanceResponse, UserResponse, UserUpdate, UserUpdatePin, UserUpdatePassword
from fastapi.exceptions import HTTPException

router = APIRouter(
    prefix='/api/v1/accounts',
    tags=['Accounts'],
    responses={404: {"description": "Not found"}},
)

@router.get('/balance', response_model=UserBalanceResponse)
def get_user_balance(current_user: User = Depends(get_current_user), db:Session = Depends(get_db)):
    wallet = current_user.wallet

    balance_response = UserBalanceResponse(
        balance=wallet.balance,
        currency=wallet.currency
    )

    # balance_response = balance_response.update_balance_with_conversion(db, wallet, wallet.currency)
    return wallet


@router.put('/update', response_model=UserResponse)
def update_user_informmation(user_update: UserUpdate, user: User = Depends(get_current_user), db:Session = Depends(get_db)):
    
    if user_update.username:
        user.username = user_update.username
    if user_update.email:
        user.email = user_update.email
    if user_update.first_name:
        user.first_name = user_update.first_name
    if user_update.last_name:
        user.last_name = user_update.last_name
    if user_update.date_of_birth:
        user.date_of_birth = user_update.date_of_birth
    if user_update.place_of_birth:
        user.place_of_birth = user_update.place_of_birth
    if user_update.physical_address:
        user.physical_address = user_update.physical_address
    if user_update.postal_code:
        user.postal_code = user_update.postal_code
    if user_update.address_proof:
        user.address_proof = user_update.address_proof
    if user_update.id_document:
        user.id_document = user_update.id_document
    if user_update.language:
        user.language = user_update.language

    db.add(user)
    db.commit()
    db.refresh(user)

    print(user.language)

    return user

@router.post('/change-pin', response_model=UserResponse)
def change_user_pin(user: UserUpdatePin, current_user: User = Depends(get_current_user), db:Session = Depends(get_db)):
    # check if pin is correct
    if not verify_pwd(user.old_pin, current_user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")

    current_user.pin = secure_pwd(user.new_pin)


    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    sendsms(current_user.phone_number, f"Votre nouveau code PIN est : {user.new_pin}")
    return current_user


@router.post("/change-password", response_model=UserResponse)
def change_password(user: UserUpdatePassword, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # check if old password is correct
    if not verify_pwd(user.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Invalid Password")

    # update password
    current_user.password = secure_pwd(user.new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
