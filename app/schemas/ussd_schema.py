from pydantic import BaseModel
from typing import Optional

class USSDRequestSchema(BaseModel):
    sessionid: str
    msisdn: str
    message: Optional[str] = None
    # serviceCode: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "sessionid": "1234567890",
                "msisdn": "237691882411",
                "message": "*123#",
                # "serviceCode": "*123#"
            }
        }


class USSDResponseSchema(BaseModel):
    message: str
    command: str  # 'CON' pour continuer la session ou 'END' pour terminer

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Bienvenue sur PerfectPay\n1. Inscription\n2. Transfert\n3. Retrait\n4. Consultation de solde",
                "command": "CON"
            }
        }
