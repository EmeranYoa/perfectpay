from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SessionCreate(BaseModel):
    session_id: str
    user_id: int
    state: str
    data: dict

    model_config={
        "json_schema_extra": {
            "example": {
                "session_id": "1234567890",
                "user_id": 1,
                "state": "state_value",
                "data": {
                    "key": "value"
                }
            }
        }
    }

class SessionUpdate(BaseModel):
    state: Optional[str] = None
    data: Optional[dict] = None

    model_config={
        "json_schema_extra": {
            "example": {
                "state": "state_value",
                "data": {
                    "key": "value"
                }
            }
        }
    }

class SessionResponse(BaseModel):
    id: int
    session_id: str
    user_id: int
    state: str
    data: dict
    is_active: bool
    last_activity: datetime
    expiration: datetime

    class Config:
        from_attributes = True

        json_schema_extra = {
            "example": {
                "id": 1,
                "session_id": "1234567890",
                "user_id": 1,
                "state": "state_value",
                "data": {
                    "key": "value"
                },
                "is_active": True,
                "last_activity": "2023-09-10T12:34:56",
                "expiration": "2023-09-10T12:34:56"
            }
        }