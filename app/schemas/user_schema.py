from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    phone_number: str
    pin: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "phone_number": "237691882411",
                "pin": "123456",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "merchant_id": 1
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
                "name": "John Doe",
                "email": "john.doe@example.com",
                "merchant_id": 1,
                "business_name": "Mon Marché"
            }
        }
    }


# Schéma pour la réponse utilisateur
class UserResponse(BaseModel):
    id: int
    phone_number: str
    name: Optional[str]
    email: Optional[EmailStr]
    language: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "phone_number": "237691882411",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "language": "fr",
                "created_at": "2022-01-01T00:00:00",
                "updated_at": "2022-01-01T00:00:00"
            }
        }


class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com"
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
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                }
            }
        }


class UserBalanceResponse(BaseModel):
    balance: float

    class Config:
        from_attributes = True
        json_schema_extra = {
            "exemple": {
                "balance": 500000
            }
        }
