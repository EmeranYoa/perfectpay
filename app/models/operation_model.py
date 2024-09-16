from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from configs.database import Base
from schemas.operation_schema import OperationCreate
from sqlalchemy.orm import Session
from models.client_model import get_client

class Operation(Base):
    __tablename__ = 'operations'
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    target_phone = Column(String(15))
    type = Column(String(50))
    amount = Column(Float)
    fees = Column(Float, default=0)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    client = relationship("Client")

def create_operation(db: Session, operation: OperationCreate):
    client = get_client(db, operation.from_phone)
    db_operation = Operation(client_id=client.id, target_phone=operation.from_phone,  amount=operation.amount, type=operation.type, status=operation.status)
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    return db_operation

def get_client_transactions(db: Session, phone_number: str):
    client = get_client(db, phone_number)
    return db.query(Operation).filter(Operation.client_id == client.id).all()