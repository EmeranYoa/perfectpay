from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint, Date
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

from app.configs.database import Base
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
    currency = Column(String(3), default="USD")

    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    owner = relationship("User", back_populates="wallet", uselist=False, foreign_keys=[owner_id])

    def convert_balance(self,  db: Session, to_currency: str) -> float:
        return convert_currency(db, self.balance, self.currency, to_currency)

    def convert_amount(self, db: Session, amount: float,  to_currency: str) -> float:
        return convert_currency(db, amount, self.currency, to_currency)

class PaymentCard(Base):
    __tablename__ = 'payment_cards'
    id = Column(Integer, primary_key=True, index=True)
    last_four_digits = Column(String(255), nullable=False)
    card_type = Column(String(20), nullable=False)  # e.g., "Visa" | "Mastercard" | "Amex"
    expiration_month = Column(Integer, nullable=False)
    expiration_year = Column(Integer, nullable=False)
    tms_token = Column(String(255), nullable=False)  # Tokenized payment card data
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    owner = relationship("User", back_populates="payment_cards", uselist=False, foreign_keys=[owner_id])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CurrencyRate(Base):
    __tablename__ = 'currency_rates'
    id = Column(Integer, primary_key=True, index=True)
    from_currency = Column(String(3), nullable=False)  # e.g., "USD"
    to_currency = Column(String(3), nullable=False)    # e.g., "EUR"
    rate = Column(Float, nullable=False)  # Conversion rate, e.g., 0.85 for USD to EUR

    __table_args__ = (
        UniqueConstraint('from_currency', 'to_currency', name='_from_to_currency_uc'),
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CurrencyRate {self.from_currency} to {self.to_currency} = {self.rate}>"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    pin = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password = Column(String(255), nullable=True)
    language = Column(String(10), default=LANGUAGES.FR.value)

    first_name = Column(String(255))
    last_name = Column(String(255))
    avatar = Column(String(255), nullable=True) # URL to avatar image
    date_of_birth = Column(Date)
    place_of_birth = Column(String(255), nullable=True)
    physical_address = Column(String(255))
    postal_code = Column(String(10), nullable=True)
    address_proof = Column(String(255), nullable=True)  # Path to proof of address file
    id_document = Column(String(255), nullable=True)  # Path to ID document file

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
    sessions = relationship("Session", back_populates="user", foreign_keys=[SessionModel.user_id])
    registered_merchants = relationship("Merchant", foreign_keys=[Merchant.registered_by], back_populates="registered_by_user")
    registered_clients = relationship("Client", foreign_keys=[Client.registered_by], back_populates="registered_by_user")

def generate_username(db: Session, first_name: str, last_name: str) -> str:
    base_username = f"{first_name.lower()}.{last_name.lower()}"
    username = base_username
    counter = 1

    # Ensure the username is unique
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    return username

def get_user(db: Session, phone_number: str):
    return db.query(User).filter(User.phone_number == phone_number).first()

def create_user(db: Session, user: UserCreate, registered_by: int = None):
    if not user.username:
        user.username = generate_username(db, user.first_name, user.last_name)

    db_client = User(**user.dict())

    db.add(db_client)
    db.flush()

    # determine the currency based on the phone number (+237, +1, and +33)
    currency = "USD"
    if user.phone_number.startswith("+237"):
        currency = "XAF"
    if user.phone_number.startswith("+33"):
        currency = "EUR"


    new_wallet = Wallet(
        owner_id=db_client.id,
        currency=currency
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

def create_merchant_user(db: Session, user: MerchantCreate, merchant_code: str, registered_by: int = None):
    b_name: str = user.business_name

    del user.business_name

    db_client = User(**user.dict())

    db.add(db_client)
    db.flush()

    new_wallet = Wallet(
        owner_id=db_client.id
    )

    new_merchant = Merchant(
        owner_id=db_client.id,
        merchant_code=merchant_code,
        email=user.email if user.email else "",
        phone_number=user.phone_number,
        business_name=b_name,
        registered_by=registered_by
    )

    db.add_all([new_wallet, new_merchant])

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

def convert_currency(db: Session, amount: float, from_currency: str, to_currency: str) -> float:
    # Check if the exchange rate exists in the database
    currency_rate = db.query(CurrencyRate).filter(
        CurrencyRate.from_currency == from_currency,
        CurrencyRate.to_currency == to_currency
    ).first()

    if not currency_rate:
        raise ValueError(f"Exchange rate from {from_currency} to {to_currency} not found.")

    # Convert the amount using the exchange rate
    converted_amount = amount * currency_rate.rate
    return converted_amount
