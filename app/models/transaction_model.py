from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.configs.database import Base


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    fees = Column(Float, nullable=False, default=0.0)
    transaction_type = Column(String(20), nullable=False)  # e.g., 'transfer', 'payment'
    status = Column(String(20), default="pending")
    currency = Column(String(3), nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="transactions", foreign_keys=[user_id])

    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Transfer to another user
    recipient = relationship("User", foreign_keys=[recipient_id])

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, transaction_type={self.transaction_type}, status={self.status}, currency={self.currency}, user_id={self.user_id}, recipient_id={self.recipient_id}, created_at={self.created_at}, updated_at={self.updated_at})>"