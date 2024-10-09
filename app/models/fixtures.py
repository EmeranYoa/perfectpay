from fastapi import Depends
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.core.utils import secure_pwd, generate_pin_code
from app.models.user_model import create_admin, User
from app.schemas.user_schema import UserCreate


def create_fixtures(db: Session):
    pin = "14952"
    passwd = 'test'
    phone_number = '237691489490'

    # check if admin exists
    admin = db.query(User).filter(phone_number == User.phone_number).first()
    if admin:
        return

    print("** Creating admin user **")

    create_admin(db, UserCreate(
        phone_number=phone_number,
        name="Test User",
        email="test@gmail.com",
        password=secure_pwd(passwd),
        pin=secure_pwd(pin)
    ))


