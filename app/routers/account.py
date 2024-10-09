from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.core.oauth import get_current_user
from app.core.send_sms import sendsms
from app.core.utils import verify_pwd, secure_pwd
from app.models.user_model import User
from app.schemas.user_schema import UserBalanceResponse, UserResponse, UserUpdate,UserUpdatePin
from fastapi.exceptions import HTTPException

router = APIRouter(
    prefix='/api/v1/accounts',
    tags=['Accounts'],
    responses={404: {"description": "Not found"}},
)

@router.get('/balance', response_model=UserBalanceResponse)
def get_user_balance(current_user: User = Depends(get_current_user)):
    wallet = current_user.wallet

    return wallet

@router.put('/update', response_model=UserResponse)
def update_user_informmation(user: UserUpdate, current_user: User = Depends(get_current_user), db:Session = Depends(get_db)):
    if user.name:
        current_user.name = user.name
    if user.email:
        current_user.email = user.email

    db.commit()
    db.refresh(current_user)

    return current_user

@router.post('/change-pin', response_model=UserResponse)
def change_user_pin(user: UserUpdatePin, current_user: User = Depends(get_current_user), db:Session = Depends(get_db)):
    # check if pin is correct
    if not verify_pwd(user.old_pin, current_user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")

    current_user.pin = secure_pwd(user.new_pin)



    db.commit()
    db.refresh(current_user)

    sendsms(current_user.phone_number, f"Votre nouveau code PIN est : {user.new_pin}")
    return current_user

