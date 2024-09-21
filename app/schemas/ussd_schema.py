from pydantic import BaseModel

class USSDRequestSchema(BaseModel):
    sessionid: str
    msisdn: str
    message: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "sessionid": "1234567890",
                "msisdn": "237691882411",
                "message": "1"
            }
        }
    }

class USSDResponseSchema(BaseModel):
    message: str
    command: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Bienvenue sur PerfectPay\n1-Transfert\n2-Retrait\n3-Paiement services\n4-Vendre\n5-Acheter\n6-Solde\n7-Paiement\n8-Recharger",
                "command": "CON"
            }
        }
    }