from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

from app.configs.database import Base
from app.models.api_key_model import APIKey
from app.models.roles_model import Merchant, Partner, Client, Admin
from app.models.session_model import Session as SessionModel
from app.models.transaction_model import Transaction
from app.schemas.user_schema import MerchantCreate, UserCreate


class LANGUAGES (Enum):
    EN = "en"
    FR = "fr"

class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="wallet", uselist=False, foreign_keys=[owner_id])

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    pin = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password = Column(String(255), nullable=True)
    language = Column(String(10), default=LANGUAGES.FR.value)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships with other entities
    wallet = relationship("Wallet", back_populates="owner", uselist=False)
    merchant = relationship("Merchant", back_populates="owner", foreign_keys="[Merchant.owner_id]", uselist=False)
    client = relationship("Client", back_populates="owner", foreign_keys="[Client.owner_id]", uselist=False)
    partner = relationship("Partner", back_populates="owner", foreign_keys="[Partner.owner_id]", uselist=False)
    admin = relationship("Admin", back_populates="owner",  foreign_keys="[Admin.owner_id]", uselist=False)


    # Registered entities by this user
    transactions = relationship("Transaction", back_populates="user", foreign_keys=[Transaction.user_id])
    api_keys = relationship("APIKey", back_populates="user", foreign_keys=[APIKey.user_id])
    sessions = relationship("Session", back_populates="user", foreign_keys=[SessionModel.user_id])
    registered_merchants = relationship("Merchant", foreign_keys=[Merchant.registered_by], back_populates="registered_by_user")
    registered_clients = relationship("Client", foreign_keys=[Client.registered_by], back_populates="registered_by_user")


def get_user(db: Session, phone_number: str):
    return db.query(User).filter(User.phone_number == phone_number).first()

def create_user(db: Session, user: UserCreate, registered_by: int):
    db_client = User(**user.dict())

    db.add(db_client)
    db.flush()

    new_wallet = Wallet(
        owner_id=db_client.id
    )

    new_client = Client(owner_id=db_client.id, registered_by=registered_by)

    db.add_all([new_wallet, new_client])

    db.commit()

    db.refresh(db_client)

    return db_client
    
def create_user_partner(db: Session, user: UserCreate, partner_code: str):
    db_client = User(**user.dict())

    db.add(db_client)
    db.flush()

    new_wallet = Wallet(
        owner_id=db_client.id
    )

    new_partner = Partner(
        owner_id=db_client.id,
        partner_code=partner_code,
        email=user.email if user.email else "",
        phone_number=user.phone_number
    )

    db.add_all([new_wallet, new_partner])

    db.commit()

    db.refresh(db_client)

    return db_client
    
def create_merchant_user(db: Session, user: MerchantCreate, merchant_code: str, registered_by: int):
    b_name: str = user.business_name

    del user.business_name

    db_client = User(**user.dict())

    db.add(db_client)
    db.flush()

    new_wallet = Wallet(
        owner_id=db_client.id
    )

    new_partner = Merchant(
        owner_id=db_client.id,
        merchant_code=merchant_code,
        email=user.email if user.email else "",
        phone_number=user.phone_number,
        business_name=b_name,
        registered_by=registered_by
    )

    db.add_all([new_wallet, new_partner])

    db.commit()

    db.refresh(db_client)

    return db_client


def create_admin(db: Session, user: UserCreate):
    db_client = User(**user.dict())

    db.add(db_client)
    db.flush()

    new_wallet = Wallet(
        owner_id=db_client.id
    )

    new_admin = Admin(owner_id=db_client.id)

    db.add_all([new_wallet, new_admin])

    db.commit()

    db.refresh(db_client)

    return db_client
def create_wallet(db: Session):
    wallet = Wallet(balance=0.0)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet

def increase_user_balance(db: Session, phone_number: str, amount: float):
    client = get_user(db, phone_number)
    if client:
        client.wallet.balance += amount
        db.commit()
        db.refresh(client)
    return client

def decrease_user_balance(db: Session, phone_number: str, amount: float):
    client = get_user(db, phone_number)
    if client and client.wallet.balance >= amount:
        client.wallet.balance -= amount
        db.commit()
        db.refresh(client)
    return client

