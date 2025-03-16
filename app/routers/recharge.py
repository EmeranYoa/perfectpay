from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.configs.database import get_db
from app.core.oauth import get_current_user
from app.core.send_sms import sendsms
from app.core.utils import verify_pwd
from app.models.transaction_model import Transaction
from app.models.user_model import User
from app.schemas.transaction_schema import RechargeRequest, Operator, TransactionResponse, RechareCardRequest, CheckoutSessionResponse, CreatePaymentCardRequest, PaymentCardsResponse
from app.core.stripe_payment import StripePayment

from app.configs.cybersource_config import CyberSourceConfig

router = APIRouter(
    prefix="/api/v1/recharges",
    tags=["Recharges"],
    responses={404: {"description": "Not found"}},
)

@router.post("/mobile-money", response_model=TransactionResponse)
async def recharge_using_mobile_money(data: RechargeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if PIN is correct
    if not verify_pwd(str(data.pin), user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")

    # Verify operator is supported
    if data.operator not in [Operator.ORANGE, Operator.MTN]:
        raise HTTPException(status_code=400, detail="Unsupported operator")

    try:
        # response = paycool(data.amount, user.phone_number)
        # if response["status"] != "success":
        #     raise HTTPException(status_code=400, detail="Payment failed")

        # Create credit transaction
        credit_transaction = Transaction(
            amount=data.amount,
            user_id=user.id,
            transaction_type="credit",
            status="completed"
        )
        db.add(credit_transaction)

        # Update user balance
        user.wallet.balance += data.amount
        db.commit()  # Commit changes
        db.refresh(user.wallet)  # Refresh wallet after update
        db.refresh(credit_transaction)

        # Send SMS notification
        sendsms(
            user.phone_number,
            f"Vous avez rechargé votre compte de {data.amount} FCFA. Votre nouveau solde est de {user.wallet.balance} FCFA."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Transaction failed")

    return credit_transaction

@router.post("/card", response_model=CheckoutSessionResponse)
async def recharge_using_card(data: RechareCardRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if PIN is correct
    if not verify_pwd(str(data.pin), user.pin):
        raise HTTPException(status_code=400, detail="Invalid PIN")

    # get user currency
    currency = user.wallet.currency

    min_amount = 5 # for default currency (usd)

    if currency == "XAF":
        min_amount = 500

    if currency == "EUR":
        min_amount = 5

    # Check if amount is valid
    if data.amount < min_amount:
        raise HTTPException(status_code=400, detail="Invalid amount")

    # make data.amount to valid stripe integer
    data.amount = int(data.amount) * 100

    # create checkout session
    stripe = StripePayment()

    metadata = {
        "user_id": user.id,
        "amount": data.amount,
        "currency": currency
    }

    # TODO: add dynamic country code
    country_code = "US"
    session = stripe.create_payment_intent(data.amount, currency, metadata=metadata)

    if not session:
        raise HTTPException(status_code=500, detail="Payment failed")


    return session

# @router.post('payment-cards', response_model=PaymentCardsResponse)
# async def create_payment_cards(data: CreatePaymentCardRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     pass

# @router.get('payment-cards', response_model=PaymentCardsResponse)
# async def get_payment_cards(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     pass

# @router.delete('payment-card/{card_id}', response_model=PaymentCardsResponse)
# async def delete_payment_cards(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     pass

# @router.get('payment-card/{card_id}', response_model=PaymentCardsResponse)
# async def get_payment_card(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     pass

# @router.put('payment-card/{card_id}', response_model=PaymentCardsResponse)
# async def update_payment_card(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     pass



from CyberSource import ApiClient, PaymentsApi
from CyberSource.rest import ApiException
from CyberSource.models import CreatePaymentRequest, Ptsv2paymentsClientReferenceInformation, Ptsv2paymentsPaymentInformationCard,Ptsv2paymentsPaymentInformation,Ptsv2paymentsOrderInformation, Ptsv2paymentsOrderInformationAmountDetails, Ptsv2paymentsOrderInformationBillTo
from app.configs.config import settings
from app.configs.cybersource_config import CyberSourceConfig
from pydantic import BaseModel, constr, conint, PositiveFloat, EmailStr
import json
import uuid


class PaymentCardData(BaseModel):
    number: constr(strip_whitespace=True, min_length=12, max_length=19)
    exp_month: conint(gt=0, le=12)
    exp_year: conint(ge=2023, le=2100)
    cvv: constr(strip_whitespace=True, min_length=3, max_length=4)
    amount: PositiveFloat
    currency: constr(strip_whitespace=True, min_length=3, max_length=3)
    first_name: constr(strip_whitespace=True, min_length=2)
    last_name: constr(strip_whitespace=True, min_length=2)
    email: EmailStr
    # Add required fields
    address: constr(min_length=1)
    city: constr(min_length=1)
    country: constr(min_length=2, max_length=2)  # ISO country code
    administrative_area: constr(min_length=1) # State or province
    postal_code: constr(min_length=3, max_length=10) # ZIP or postal code

def del_none(d):
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d

@router.post("/test")
async def test(card_data: PaymentCardData, db: Session = Depends(get_db)):
    try:
        card_dict = card_data.dict()
        logger.debug(f"Données reçues : {card_dict}")
        config = CyberSourceConfig().get_configuration()
        api_client = ApiClient()
        api_client.set_configuration(config)

        client_ref_info = Ptsv2paymentsClientReferenceInformation(
            code=f"PAY-{uuid.uuid4().hex[:10]}"  # Unique reference
        )

        card_info = Ptsv2paymentsPaymentInformationCard(
            number=card_data.number,
            expiration_month=f"{card_data.exp_month:02d}",
            expiration_year=str(card_data.exp_year)[-2:],
            security_code=card_data.cvv
        )

        amount_details = Ptsv2paymentsOrderInformationAmountDetails(
            total_amount=f"{card_data.amount:.2f}",
            currency=card_data.currency.upper()
        )

        bill_to = Ptsv2paymentsOrderInformationBillTo(
            first_name=card_data.first_name,
            last_name=card_data.last_name,
            email=card_data.email,
            address1=card_data.address,
            locality=card_data.city,
            country=card_data.country,
            administrative_area=card_data.administrative_area,
            postal_code=card_data.postal_code
        )

        payment_request = CreatePaymentRequest(
            client_reference_information=client_ref_info.__dict__,
            payment_information=Ptsv2paymentsPaymentInformation(card=card_info.__dict__).__dict__,
            order_information=Ptsv2paymentsOrderInformation(
                amount_details=amount_details.__dict__,
                bill_to=bill_to.__dict__
            ).__dict__
        )

        payment_request = del_none(payment_request.__dict__)
        payment_request = json.dumps(payment_request)


        payments_api = PaymentsApi(config)
        data, status, body = payments_api.create_payment(payment_request)

        if status == 201:
            return {
                "status": status,
                "message": "Payment successful",
                "data": data
            }

        return {
            "status": status,
            "message": "Payment failed",
            "data": data
        }

    except ApiException as e:
        error_info = {}
        logger.error(f"Error: {e.body}")
        try:
            error_info["status"] = json.loads(e.body).get("status", "PAYMENT_FAILED")
            error_info["reason"] = json.loads(e.body).get("reason", "PAYMENT_FAILED")
            error_info["message"] = json.loads(e.body).get("message", "Payment processing failed")
            error_info["details"] = json.loads(e.body).get("details", {})
        except json.JSONDecodeError:
            error_info = {"message": str(e.body)}

        logger.error(f"CyberSource Error: {error_info}")
        status_code = 400 if e.status in [400, 422] else 502
        raise HTTPException(
            status_code=status_code,
            detail={
                "status": error_info.get("status", "PAYMENT_FAILED"),
                "reason": error_info.get("reason", "PAYMENT_FAILED"),
                "message": error_info.get("message", "Payment processing failed"),
                "data": error_info.get("details", {})
            }
        )

    except Exception as e:
        logger.error(f"Erreur système: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur"
        )
