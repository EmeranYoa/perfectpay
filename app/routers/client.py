import random
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from schemas.client_schema import ClientBase, ClientCreate, TransferRequest, TransferResponseSchema, SoldeRequest, SoldeResponse, RechargeRequest, RechargeResponse, ClientCreateResponseSchema
from schemas.operation_schema import OperationResponse, OperationCreate
from configs.database import get_db
from configs.config import settings
from models.client_model import Client, get_client, create_client, increase_client_balance
from models.operation_model import get_client_transactions, create_operation
from core.send_sms import sendsms
from core.paycool import paycool

router = APIRouter(
    prefix="/api/v1",
    tags=["basic-operations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/clients", response_model=ClientCreateResponseSchema)
def create_new_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = get_client(db, client.phone_number)
    if db_client:
        raise HTTPException(status_code=400, detail="Client already exists")
    
    if client.pin == None:
        client.pin = str(random.randint(10000, 99999))
    new_client = create_client(db, client)
    sendsms(client.phone_number, f"Bienvenue sur {settings.PROJECT_NAME}.\nVotre code pin est le {client.pin}")
    return new_client

@router.post("/transfer", response_model=TransferResponseSchema)
def transfer_money(transfer: TransferRequest, db: Session = Depends(get_db)):
    sender = get_client(db, transfer.from_phone)
    receiver = get_client(db, transfer.to_phone)

    if not sender or sender.pin != transfer.pin:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    if sender.balance < transfer.amount:
        sendsms(sender.phone_number, f"Vous n'avez pas assez de solde pour effectuer cette transaction.")
        raise HTTPException(status_code=400, detail="Insufficient balance")

    if not receiver:
        sendsms(sender.phone_number, f"Le numéro {transfer.to_phone} n'existe pas.")
        raise HTTPException(status_code=404, detail="Receiver not found")

    sender.balance -= transfer.amount
    receiver.balance += transfer.amount

    db.commit()

    operation = OperationCreate(
        from_phone=sender.phone_number,
        to_phone=receiver.phone_number,
        amount=transfer.amount,
        status="success",
        type="transfer"
    )

    create_operation(db, operation)

    sendsms(sender.phone_number, f"Vous avez transféré {transfer.amount} FCFA. au numéro {transfer.to_phone}.")
    sendsms(receiver.phone_number, f"Vous avez reçu {transfer.amount} FCFA de {sender.phone_number}.")

    return {"message": "Transfer successful"}

@router.post("/solde", response_model=SoldeResponse)
def get_solde(request: SoldeRequest, db: Session = Depends(get_db)):
    client = get_client(db, request.phone_number)
    if not client or client.pin != request.pin:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    return {"solde": client.balance}


@router.post("/recharge", response_model=RechargeResponse)
def recharge_account(request: RechargeRequest, db: Session = Depends(get_db)):
    client = get_client(db, request.phone_number)
    if not client or client.pin != request.pin:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    
    response = paycool(request.amount, client.phone_number)

    if response.get("status") != "success":
        raise HTTPException(status_code=400, detail="Recharge failed")
    
    increase_client_balance(db, client.phone_number, request.amount)

    operation = OperationCreate(
        from_phone=request.phone_number,
        to_phone=request.phone_number,
        amount=request.amount,
        status="success",
        type="recharge"
    )

    create_operation(db, operation)

    return {"message": "Recharge successful"}


@router.post("/history", response_model=list[OperationResponse])
def get_transaction_history(request: ClientBase,db: Session = Depends(get_db)):
    client = get_client(db, request.phone_number)
    if not client or client.pin != request.pin:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    history = get_client_transactions(db, request.phone_number)

    return history