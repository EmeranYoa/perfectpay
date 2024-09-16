from pydantic import BaseModel

class OperationCreate(BaseModel):
    to_phone: str
    from_phone: str
    amount: float
    type: str
    status: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "to_phone": "237691882411",
                "from_phone": "237699999999",
                "amount": 1000,
                "type": "transfer",
                "status": "success"
            }
        }
    }

class OperationResponse(BaseModel):
    id: int
    status: str
    amount: float
    target_phone: str
    fees: float
    class Config:
        from_attributes = True
        
        json_schema_extra = {
            "example": {
                "id": 1,
                "status": "success",
                "target_phone": "237699999999",
                "amount": 1000,
                "fees": 10,
            }
        }