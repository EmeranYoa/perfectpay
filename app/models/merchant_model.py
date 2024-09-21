from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from configs.database import Base

class Merchant(Base):
    __tablename__ = 'merchants'
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    merchant_code = Column(String(255), unique=True, nullable=False)

    owner = relationship("User", back_populates="merchant", uselist=False)

def get_merchant(db, phone_number):
    return db.query(Merchant).filter(Merchant.phone_number == phone_number).first()