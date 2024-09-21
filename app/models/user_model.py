from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from configs.database import Base
from  datetime import datetime
from sqlalchemy.orm import Session
from schemas.user_schema import UserCreate
from sqlalchemy.orm import relationship

class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    owner = relationship("User", back_populates="wallet", uselist=False)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    pin = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password = Column(String(255), nullable=True)
    
    wallet_id = Column(Integer, ForeignKey('wallets.id'))
    wallet = relationship("Wallet", back_populates="owner")

    merchant_id = Column(Integer, ForeignKey('merchants.id'), nullable=True)
    merchant = relationship("Merchant", back_populates="owner", foreign_keys=[merchant_id])

    transactions = relationship("Transaction", back_populates="user", foreign_keys="[Transaction.user_id]")
    api_keys = relationship("APIKey", back_populates="user", foreign_keys="[APIKey.user_id]")

    sessions = relationship("Session", back_populates="user", foreign_keys="[Session.user_id]")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_user(db: Session, phone_number: str):
    return db.query(User).filter(User.phone_number == phone_number).first()

def create_user(db: Session, user: UserCreate):
    db_client = User(**user.dict())

    wallet = create_wallet(db)
    
    db_client.wallet_id = wallet.id

    db.add(db_client)
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

