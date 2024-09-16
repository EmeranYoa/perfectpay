from sqlalchemy import Column, Integer, String, DateTime
from configs.database import Base
from  datetime import datetime
from sqlalchemy.orm import Session
from schemas.client_schema import ClientCreate

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), index=True, unique=True, nullable=False) 
    pin = Column(String(6), index=True, nullable=False)
    balance = Column(Integer, default=0, index=True, nullable=False) 
    type = Column(String(50), index=True, default="client", nullable=False)
    address = Column(String(255), index=True)
    market_code = Column(String(50), index=True)
    status = Column(String(50), index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100))
    sponsor = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_client(db: Session, phone_number: str):
    return db.query(Client).filter(Client.phone_number == phone_number).first()

def create_client(db: Session, client: ClientCreate):
    db_client = Client(phone_number=client.phone_number, pin=client.pin, password=client.pin)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def increase_client_balance(db: Session, phone_number: str, amount: float):
    client = get_client(db, phone_number)
    if client:
        client.balance += amount
        db.commit()
        db.refresh(client)
    return client

def decrease_client_balance(db: Session, phone_number: str, amount: float):
    client = get_client(db, phone_number)
    if client and client.balance >= amount:
        client.balance -= amount
        db.commit()
        db.refresh(client)
    return client