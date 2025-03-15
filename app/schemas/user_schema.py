from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from fastapi import Form, UploadFile
class UserCreate(BaseModel):
    phone_number: str
    pin: Optional[str] = None
    username: Optional[str] = None
    email: EmailStr
    password: Optional[str] = None
    first_name: str
    last_name: str
    avatar: Optional[str] = None  # Path to avatar file
    date_of_birth: date
    place_of_birth: str
    physical_address: Optional[str] = None
    postal_code: Optional[str] = None
    address_proof: Optional[str] = None  # Path to address proof
    id_document: Optional[str] = None  # Path to ID document
    
    # Optional: If you want to use language as well
    language: Optional[str] = None  # Default value is set at the model level

    @classmethod
    def as_form(
        cls,
        phone_number: str = Form(...),
        pin: Optional[str] = Form(None),
        email: EmailStr = Form(...),
        password: Optional[str] = Form(None),
        first_name: str = Form(...),
        last_name: str = Form(...),
        date_of_birth: date = Form(...),
        place_of_birth: str = Form(...),
        physical_address: Optional[str] = Form(None),
        postal_code: Optional[str] = Form(None),
        language: Optional[str] = Form(None),
    ):
        """
        This classmethod allows us to parse the model fields from `multipart/form-data` directly.
        """
        return cls(
            phone_number=phone_number,
            pin=pin,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            place_of_birth=place_of_birth,
            physical_address=physical_address,
            postal_code=postal_code,
            language=language,
        )

    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "237691882411",
                "pin": "123456",
                "username": "john.doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "avatar": "/path/to/avatar.jpg",
                "date_of_birth": "1990-05-15",
                "place_of_birth": "Yaoundé",
                "physical_address": "123 Main St, Yaoundé",
                "postal_code": "12345",
                "address_proof": "/path/to/address/proof.jpg",
                "id_document": "/path/to/id/document.jpg",
                "language": "fr",
            }
        }
    }


class MerchantCreate(UserCreate):
    business_name: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "237691882411",
                "pin": "123456",
                "username": "john.doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "avatar": "/path/to/avatar.jpg",
                "date_of_birth": "1990-05-15",
                "place_of_birth": "Yaoundé",
                "physical_address": "123 Main St, Yaoundé",
                "postal_code": "12345",
                "address_proof": "/path/to/address/proof.jpg",
                "id_document": "/path/to/id/document.jpg",
                "language": "fr",
                "business_name": "John's Business"
            }
        }
    }


# Schéma pour la réponse utilisateur
class UserResponse(BaseModel):
    id: int
    phone_number: str
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    avatar: Optional[str] # Path to avatar file
    date_of_birth: date
    place_of_birth: str
    physical_address: Optional[str]
    postal_code: Optional[str]
    address_proof: Optional[str]  # Path to address proof file
    id_document: Optional[str]  # Path to ID document file
    language: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "phone_number": "237691882411",
                "username": "john.doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "avatar": "/path/to/avatar.jpg",
                "date_of_birth": "1990-05-15",
                "place_of_birth": "Yaoundé",
                "physical_address": "123 Main St, Yaoundé",
                "postal_code": "12345",
                "address_proof": "/path/to/address/proof.jpg",
                "id_document": "/path/to/id/document.jpg",
                "language": "fr",
                "created_at": "2022-01-01T00:00:00",
                "updated_at": "2022-01-01T00:00:00"
            }
        }


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None  # Path to avatar file
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None
    physical_address: Optional[str] = None
    postal_code: Optional[str] = None
    address_proof: Optional[str] = None  # Path to address proof
    id_document: Optional[str] = None  # Path to ID document
    
    language: Optional[str] = None  # Optional update for language

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "john.doe",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "avatar": "/path/to/avatar.jpg",
                "date_of_birth": "1990-05-15",
                "place_of_birth": "Yaoundé",
                "physical_address": "123 Main St, Yaoundé",
                "postal_code": "12345",
                "address_proof": "/path/to/address/proof.jpg",
                "id_document": "/path/to/id/document.jpg",
                "language": "fr",
            }
        }
    }


class UserUpdatePin(BaseModel):
    old_pin: str
    new_pin: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "old_pin": "123456",
                "new_pin": "654321"
            }
        }
    }

class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "old_password": "old_password",
                "new_password": "new_password"
            }
        }
    }


# Schéma pour l'authentification
class UserLogin(BaseModel):
    phone_number: str
    # require pin or password
    pin: Optional[str] = None
    password: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "237691882411",
                "pin": "123456"
            }
        }
    }


# Schéma pour la réponse de l'authentification
class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "phone_number": "237691882411",
                    "username": "john.doe",
                    "email": "john.doe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "avatar": "/path/to/avatar.jpg",
                    "date_of_birth": "1990-05-15",
                    "place_of_birth": "Yaoundé",
                    "physical_address": "123 Main St, Yaoundé",
                    "postal_code": "12345",
                    "address_proof": "/path/to/address/proof.jpg",
                    "id_document": "/path/to/id/document.jpg",
                    "language": "fr", 
                }
            }
        }


class UserBalanceResponse(BaseModel):
    balance: float
    currency: str # Currency code (e.g., USD, EUR, XAF)
    converted_balance: Optional[float] = None 
    conversion_currency: Optional[str] = None 


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "balance": 5000.0,
                "currency": "USD",
                "converted_balance": 4250.0,
                "conversion_currency": "EUR"
            }
        }

    def update_balance_with_conversion(self,db,  user_wallet, to_currency: str,) -> None:
        """
        This method updates the balance with the converted value if the currency differs.
        """
        # Fetch the user's wallet balance and currency
        self.balance = user_wallet.balance
        self.currency = user_wallet.currency

        # If the desired currency for conversion is different, perform the conversion
        if self.currency != to_currency:
            self.converted_balance = user_wallet.convert_balance(db, to_currency)
            self.conversion_currency = to_currency
        else:
            self.converted_balance = self.balance
            self.conversion_currency = self.currency
