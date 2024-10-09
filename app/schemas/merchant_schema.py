from typing import Optional

from pydantic import BaseModel, EmailStr

from app.schemas.user_schema import UserCreate, UserUpdate


# Schéma pour un merchant
class MerchantCreate(BaseModel):
    business_name: str
    phone_number: str
    email: EmailStr
    owner: UserCreate

    
    model_config = {
        "from_attributes":True,
        "json_schema_extra": {
            "example": {
                "business_name": "Mon Marché",
                "phone_number": "237691882411",
                "email": "monmarché@example.com",
                "owner": {
                    "phone_number": "237691882411",
                    "pin": "123456",
                    "name": "John Doe",
                    "email": "john.doe@example.com"
                }
            }
        }
    }

class MerchantUpdate(BaseModel):
    business_name: Optional[str]
    phone_number: Optional[str]
    email: Optional[EmailStr]
    owner: Optional[UserUpdate]

    model_config = {
        "from_attributes":True,
        "json_schema_extra": {
            "example": {
                "business_name": "Mon Marché",
                "phone_number": "237691882411",
                "email": "monmarché@example.com",
                "owner": {
                    "name": "John Doe",
                    "email": "john.doe@example.com"
                }
            }
        }
    }

# Schéma pour la réponse d'un marchand
class MerchantResponse(BaseModel):
    id: int
    business_name: str
    phone_number: str
    email: EmailStr
    

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "id": 1,
                "business_name": "Mon Marché",
                "phone_number": "237691882411",
                "email": "monmarché@example.com"
            }
        }