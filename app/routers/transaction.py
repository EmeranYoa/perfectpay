from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, select
from app.configs.database import get_db
from app.configs.config import settings
from app.models.transaction_model import Transaction
from app.models.user_model import User, get_user, convert_currency
from app.models.roles_model import Merchant, get_merchant
from app.schemas.transaction_schema import TransferRequest, TransactionResponse, WithdrawRequest
from app.schemas.user_schema import  UserResponse
from app.core.oauth import get_current_user
from app.core.utils import verify_pwd
from app.core.send_sms import sendsms
from datetime import datetime, timedelta
from fastapi_pagination import Page, paginate
from app.core.stripe_payment import StripePayment

router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["Transactions"],
    responses={404: {"description": "Not found"}},
)


@router.get('/verify-recipient/{phone_number}', response_model=UserResponse)
def transfer_verify_recipient(phone_number: str, current_user: User = Depends(get_current_user), db:Session = Depends(get_db)):
    
    
    u = db.query(User).filter(User.phone_number == phone_number).first()

    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u

@router.post("/transfer", response_model=TransactionResponse)
def transfer_funds(
    transaction: TransferRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check user is different from recipient
    if user.phone_number == transaction.recipient_phone:
        raise HTTPException(status_code=400, detail="You cannot transfer funds to yourself")

    # Verify PIN
    if not verify_pwd(str(transaction.pin), user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")

    # Get recipient user with wallet loaded
    recipient_user = (
        db.query(User)
        .options(joinedload(User.wallet))
        .filter(User.phone_number == transaction.recipient_phone)
        .first()
    )
    if not recipient_user:
        raise HTTPException(status_code=404, detail="Recipient user not found")

    # Validate amount
    if transaction.amount < 50:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum transfer amount is 50 {user.wallet.currency}"
        )

    # Check sufficient funds
    if user.wallet.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    try:
        # Load both users with relationships for the response
        db.refresh(user)
        db.refresh(recipient_user)

        sender_currency = user.wallet.currency
        recipient_currency = recipient_user.wallet.currency
        
        # Handle currency conversion if needed
        converted_amount = (
            convert_currency(db, transaction.amount, sender_currency, recipient_currency)
            if sender_currency != recipient_currency
            else transaction.amount
        )

        # Create debit transaction with relationships loaded
        debit_transaction = Transaction(
            amount=transaction.amount,
            user_id=user.id,
            user=user,  # Set relationship explicitly
            transaction_type="debit",
            recipient_id=recipient_user.id,
            recipient=recipient_user,  # Set relationship explicitly
            status="completed",
            currency=sender_currency,
            created_at=datetime.utcnow()
        )

        # Update balances
        user.wallet.balance -= transaction.amount
        recipient_user.wallet.balance += converted_amount

        # Add and commit
        db.add(debit_transaction)
        db.commit()

        # Explicitly refresh with relationships
        db.refresh(debit_transaction)
        debit_transaction.user = user
        debit_transaction.recipient = recipient_user

        # Send notifications
        sendsms(
            recipient_user.phone_number,
            f"You received {converted_amount} {recipient_currency} from {user.phone_number}. New balance: {recipient_user.wallet.balance} {recipient_currency}."
        )
        sendsms(
            user.phone_number,
            f"You sent {transaction.amount} {sender_currency} to {recipient_user.phone_number}. New balance: {user.wallet.balance} {sender_currency}."
        )

        return debit_transaction

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transaction processing failed")

@router.post('/withdraw', response_model=TransactionResponse)
def withdraw_funds(transaction: WithdrawRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Vérifier si le PIN est correct
    if not verify_pwd(str(transaction.pin), user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")

    # Vérifier si l'utilisateur a suffisamment de fonds
    if user.wallet.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Vérifier si le commerçant existe avec le code du commerçant et le numéro de téléphone fournis
    merchant = get_merchant(db, transaction.merchan_phone)

    if not merchant:
        raise HTTPException(status_code=400, detail="Merchant not found or invalid merchant code")

    if not verify_pwd(str(transaction.merchant_code), merchant.merchant_code):
        raise HTTPException(status_code=400, detail="Merchant not found or invalid merchant code")

    try:
        # Récupérer le propriétaire du commerçant
        merchant_owner = db.query(User).filter(User.merchant == merchant).first()

        if not merchant_owner:
            raise HTTPException(status_code=400, detail="Merchant owner not found")

        # Obtenez les taux de change pour convertir entre les devises des deux utilisateurs
        sender_currency = user.wallet.currency
        recipient_currency = merchant_owner.wallet.currency

        # Si les devises sont différentes, effectuer la conversion
        if sender_currency != recipient_currency:
            # Calculer le montant converti
            converted_amount = convert_currency(db, transaction.amount, sender_currency, recipient_currency)
        else:
            # Si la devise de l'expéditeur et du commerçant est la même, il n'y a pas de conversion
            converted_amount = transaction.amount

        # Créer la transaction de débit pour l'utilisateur
        debit_transaction = Transaction(
            amount=transaction.amount,
            user_id=user.id,
            recipient_id=merchant_owner.id,
            transaction_type="debit",
            status="completed",
            currency=sender_currency  # Enregistrer la devise de l'utilisateur
        )

        # Créer la transaction de crédit pour le commerçant
        credit_transaction = Transaction(
            amount=converted_amount,
            user_id=merchant_owner.id,
            recipient_id=merchant_owner.id,
            transaction_type="credit",
            status="completed",
            currency=recipient_currency  # Enregistrer la devise du commerçant
        )

        # Mettre à jour les soldes des utilisateurs
        user.wallet.balance -= transaction.amount
        merchant_owner.wallet.balance += converted_amount

        # Ajouter et valider les deux transactions
        db.add(debit_transaction)
        db.add(credit_transaction)
        db.commit()  # Valider une seule fois pour toutes les modifications

        # Rafraîchir les données pour obtenir les informations mises à jour
        db.refresh(user.wallet)
        db.refresh(merchant_owner.wallet)
        db.refresh(debit_transaction)
        db.refresh(credit_transaction)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Transaction failed")

    # Envoyer un SMS à l'utilisateur et au commerçant
    sendsms(
        user.phone_number,
        f"Vous avez retiré {transaction.amount} {sender_currency}. Votre nouveau solde est de {user.wallet.balance} {sender_currency}."
    )
    sendsms(
        merchant_owner.phone_number,
        f"Vous avez reçu {converted_amount} {recipient_currency} de {user.phone_number}. Votre nouveau solde est de {merchant_owner.wallet.balance} {recipient_currency}."
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

    query = db.query(Transaction).options(
            joinedload(Transaction.user),
            joinedload(Transaction.recipient)
        ).filter(
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
    transaction = db.query(Transaction).options(
            joinedload(Transaction.user),
            joinedload(Transaction.recipient)
        ).filter(transaction_id == Transaction.id, user.id == Transaction.user_id).first()
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



@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    stripe = StripePayment()
    payload = await request.body()
    event = stripe.webhook_handler(payload, request.headers["Stripe-Signature"])
    
    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type == "payment_intent.succeeded":
        session = data_object
        print("Payment intent succeeded:", session["id"])

        metadata = session["metadata"]

        user_id = metadata["user_id"]
        amount = metadata["amount"]
        currency = metadata["currency"]

        recharge_amount = float(amount) / 100
        credit_transaction = Transaction(
            amount= recharge_amount,
            user_id=user_id,
            recipient_id=user_id,
            transaction_type="credit",
            status="completed",
            currency=currency,
        )

        db.add(credit_transaction)
        
        # get user from user_id and update wallet balance
        user = db.query(User).filter(User.id == user_id).first()
        user.wallet.balance += recharge_amount
        db.commit()  # Commit changes



        print(f"User ID: {user_id}, Amount: {amount}, Currency: {currency}")


        # TODO: send notification to user
    else:
        print(f"Unhandled event type {event_type}")

    return {"status": "success"}