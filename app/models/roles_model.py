from app.configs.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship



class Merchant(Base):
    __tablename__ = 'merchants'
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    merchant_code = Column(String(255), unique=True, nullable=False)

    # Relationship to the User who registered the Merchant (Partner or Admin)
    registered_by = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=True)
    registered_by_user = relationship("User", foreign_keys=[registered_by], back_populates="registered_merchants", uselist=False)

    # Relationship to the User who owns the Merchant (direct business owner)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    owner = relationship("User", foreign_keys=[owner_id], back_populates="merchant", uselist=False)

def get_merchant(db, phone_number):
    return db.query(Merchant).filter(Merchant.phone_number == phone_number).first()

class Partner(Base):
    __tablename__ = 'partners'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    partner_code = Column(String(255), unique=True, nullable=False)

    # Partner is associated with a User (the owner of the Partner account)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="partner", uselist=False)


class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)

    # The User who registered this Client (likely an admin or partner)
    registered_by = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=True)
    registered_by_user = relationship("User", foreign_keys=[registered_by], back_populates="registered_clients", uselist=False)

    # The owner of the Client account (direct user who is the client)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    owner = relationship("User", foreign_keys=[owner_id], back_populates="client", uselist=False)


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, index=True)

    # The User who is the Admin
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="admin", uselist=False)