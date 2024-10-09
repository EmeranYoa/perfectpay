from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, select
from app.configs.database import get_db
from app.models.transaction_model import Transaction
from app.models.user_model import User, get_user
from app.models.roles_model import Merchant, get_merchant
from app.schemas.transaction_schema import TransferRequest, TransactionResponse, WithdrawRequest
from app.core.oauth import get_current_user
from app.core.utils import verify_pwd
from app.core.send_sms import sendsms
from datetime import datetime, timedelta
from fastapi_pagination import Page, paginate

router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["Transactions"],
    responses={404: {"description": "Not found"}},
)


@router.post("/transfer", response_model=TransactionResponse)
def transfer_funds(transaction: TransferRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    #  check user is different from recipient
    if user.phone_number == transaction.recipient_phone:
        raise HTTPException(status_code=400, detail="You cannot transfer funds to yourself")

    # Verify if the PIN is correct
    if not verify_pwd(str(transaction.pin), user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")

    # Get recipient user
    recipient_user = get_user(db, transaction.recipient_phone)
    if not recipient_user:
        raise HTTPException(status_code=400, detail="Recipient user not found")

    # check if transfer amount is up to 50
    if transaction.amount < 50:
        raise HTTPException(status_code=400, detail="You can only transfer up to 50 FCFA")

    # Check if the user has sufficient funds
    if user.wallet.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    try:
        # Create debit transaction for the sender
        debit_transaction = Transaction(
            amount=transaction.amount,
            user_id=user.id,
            transaction_type="debit",
            recipient_id=recipient_user.id,
            status="completed"
        )

        # Create credit transaction for the recipient
        credit_transaction = Transaction(
            amount=transaction.amount,
            user_id=recipient_user.id,
            recipient_id=recipient_user.id,
            transaction_type="credit",
            status="completed"
        )

        # Update user and recipient balances
        user.wallet.balance -= transaction.amount
        recipient_user.wallet.balance += transaction.amount

        # Add and commit both transactions and balance updates
        db.add(debit_transaction)
        db.add(credit_transaction)

        db.commit()  # Commit once for all changes

        # Refresh to get the updated data
        db.refresh(user.wallet)
        db.refresh(recipient_user.wallet)
        db.refresh(debit_transaction)
        db.refresh(credit_transaction)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Transaction failed")

    # Send SMS to recipient and user
    sendsms(
        recipient_user.phone_number,
        f"Vous avez reçu {transaction.amount} FCFA de {user.phone_number}. Votre nouveau solde est de {recipient_user.wallet.balance} FCFA."
    )
    sendsms(
        user.phone_number,
        f"Vous avez envoyé {transaction.amount} FCFA à {recipient_user.phone_number}. Vous avez été débité de {transaction.amount} FCFA. Votre nouveau solde est de {user.wallet.balance} FCFA."
    )

    return debit_transaction


@router.post('/withdraw', response_model=TransactionResponse)
def withdraw_funds(transaction: WithdrawRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify if the PIN is correct
    if not verify_pwd(str(transaction.pin), user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")

    # Check if the user has sufficient funds
    if user.wallet.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Check if merchant exists using the provided merchant_code and phone number
    merchant = get_merchant(db, transaction.merchan_phone)

    if not merchant:
        raise HTTPException(status_code=400, detail="Merchant not found or invalid merchant code")

    if not verify_pwd(str(transaction.merchant_code), merchant.merchant_code):
        raise HTTPException(status_code=400, detail="Merchant not found or invalid merchant code")

    try:
        # get merchant owner
        merchant_owner = db.query(User).filter(User.merchant == merchant).first()

        if not merchant_owner:
            raise HTTPException(status_code=400, detail="Merchant owner not found")
        # Create debit transaction
        debit_transaction = Transaction(
            amount=transaction.amount,
            user_id=user.id,
            recipient_id=merchant_owner.id,
            transaction_type="debit",
            status="completed"
        )

        # create credit transaction
        credit_transaction = Transaction(
            amount=transaction.amount,
            user_id=merchant_owner.id,
            recipient_id=merchant_owner.id,
            transaction_type="credit",
            status="completed"
        )

        # Update merchant balance
        merchant_owner.wallet.balance += transaction.amount
        # Update user balance
        user.wallet.balance -= transaction.amount
        # Add and commit both transactions and balance updates
        db.add(debit_transaction)
        db.add(credit_transaction)
        db.commit()  # Commit once for all changes
        # Refresh to get the updated data
        db.refresh(user.wallet)
        db.refresh(merchant_owner.wallet)
        db.refresh(debit_transaction)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Transaction failed")
    # Send SMS to user and merchant
    sendsms(
        user.phone_number,
        f"Vous avez retiré {transaction.amount} FCFA. Votre nouveau solde est de {user.wallet.balance} FCFA."
    )
    sendsms(
        merchant.owner.phone_number,
        f"Vous avez reçu {transaction.amount} FCFA de {user.phone_number}. Votre nouveau solde est de {merchant.owner.wallet.balance} FCFA."
    )

    return debit_transaction


@router.get("/history", response_model=Page[TransactionResponse])
def get_transaction_history(
    user: User = Depends(get_current_user),
    start_date: datetime = Query(None, description="Filter transactions by start date"),
    end_date: datetime = Query(None, description="Filter transactions by end date"),
    db: Session = Depends(get_db)
):

    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    query = db.query(Transaction).filter(
        Transaction.created_at.between(start_date, end_date)
    )

    if not user.admin:
        query = query.filter(or_(
            Transaction.user_id == user.id,
            Transaction.recipient_id == user.id
        ))

    return paginate(query.order_by(Transaction.created_at.desc()).all())


@router.get("/history/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
        transaction_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(transaction_id == Transaction.id, user.id == Transaction.user_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post('/pay-service')
def pay_service(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Implement the logic to pay for a service
    # This could involve creating a transaction, updating user balance, etc.
    # input data: service_id, amount, pin
    # For now, just return a message
    return {"message": "Payment service coming soon"}
