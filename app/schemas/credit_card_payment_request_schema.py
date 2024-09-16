from pydantic import BaseModel

class CreditCardPaymentRequest(BaseModel):
    stripeToken: str
    customerName: str
    CustomerPhone: str
    Currency: str
    cardNumber: str
    cardCVC: str
    cardExpMonth: int
    cardExpYear: int
    ClientAddress: str
    amount: float
    itemName: str
