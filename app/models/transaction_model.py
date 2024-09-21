from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from configs.database import Base
from models.user_model import get_user

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    fees = Column(Float, nullable=False, default=0.0)
    transaction_type = Column(String(20), nullable=False)  # e.g., 'transfer', 'payment'
    status = Column(String(20), default="pending")
    
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="transactions", foreign_keys=[user_id])

    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Transfer to another user
    recipient = relationship("User", foreign_keys=[recipient_id])

    created_at = Column(DateTime, server_default=func.now())


    
# def create_transaction(db: Session, operation: OperationCreate):
#     client = get_user(db, operation.from_phone)
#     db_operation = Operation(client_id=client.id, target_phone=operation.from_phone,  amount=operation.amount, type=operation.type, status=operation.status)
#     db.add(db_operation)
#     db.commit()
#     db.refresh(db_operation)
#     return db_operation

# def get_user_transactions(db: Session, phone_number: str):
#     client = get_user(db, phone_number)
#     return db.query(Operation).filter(Operation.client_id == client.id).all()