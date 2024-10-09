from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.configs.database import Base

class Tariff(Base):
    __tablename__ = 'tariffs'
    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String(20), nullable=False)  # e.g., 'transfer', 'payment'
    min_amount = Column(Float, nullable=False)
    max_amount = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)