import stripe
from app.configs.config import settings

class StripePayment:
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe.default_api_version = "2022-08-01"
        self.endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    def create_checkout_session(self, amount, currency, success_url, cancel_url, metadata=None):
        try:
            checkout_session = self.stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": currency,
                            "unit_amount": amount,
                            "product_data": {
                                "name": "Payment",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata,
            )
            return checkout_session
        except Exception as e:
            raise e
    
    def create_payment_intent(self, amount, currency, metadata=None):
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                automatic_payment_methods={"enabled": True},
                metadata=metadata,
            )
            return {
                "clientSecret": intent.client_secret,
            }
        except Exception as e:
            raise e

    def webhook_handler(self, payload, stripe_signature):
        try:
            event = self.stripe.Webhook.construct_event(
                payload,
                stripe_signature,
                self.endpoint_secret,
            )
            return event
        except Exception as e:
            raise e