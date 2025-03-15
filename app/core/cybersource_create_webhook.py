from CyberSource import *
import os
import json
from pathlib import Path
from app.configs.config import settings
from app.configs.cybersource_config import CyberSourceConfig

# Configuration
CYBERSOURCE_CONFIG = {
    "organization_id": settings.CYBERSOURCE_MERCHANT_ID,  # Get from CyberSource Business Center
    "product_id": "payments",  # For payment notifications
    "webhook_url": "https://stirring-scarcely-hog.ngrok-free.app/api/v1/webhook",
    "health_check_url": "https://stirring-scarcely-hog.ngrok-free.app/api/v1/webhook-healthcheck",
    "webhook_secret": settings.CYBERSOURCE_WEBHOOK_SECRET,
    "event_types": [
        "payments.payments.created",
        "payments.payments.updated",
        "payments.captures.created"
    ]
}

def create_wallet_webhook():
    # Configure webhook request
    requestObj = CreateWebhookRequest(
        name="Perfect Pay webhook (local environment)",
        description="Parfect Pay Payments Getway Webhook for local environment",
        organization_id=CYBERSOURCE_CONFIG["organization_id"],
        product_id=CYBERSOURCE_CONFIG["product_id"],
        event_types=CYBERSOURCE_CONFIG["event_types"],
        webhook_url=CYBERSOURCE_CONFIG["webhook_url"],
        health_check_url=CYBERSOURCE_CONFIG["health_check_url"],
        notification_scope="SELF",
        retry_policy=Notificationsubscriptionsv1webhooksRetryPolicy(
            algorithm="ARITHMETIC",
            first_retry=1,
            interval=1,
            number_of_retries=3,
            deactivate_flag="false"
        ).__dict__,
        security_policy=Notificationsubscriptionsv1webhooksSecurityPolicy1(
            security_type="HMAC_SHA256",  # Use HMAC_SHA256 for signed notifications
            proxy_type="external"
        ).__dict__
    )

    # Clean None values and convert to JSON
    request_body = json.dumps(clean_request(requestObj.__dict__))

    try:
        # Initialize API client
        config = CyberSourceConfig().get_configuration()

        api_instance=  ManageWebhooksApi(config)
        response, status, body = api_instance.get_webhook_subscription_by_id("2f67d137-4ad1-8372-e063-9e588e0a7cf0")

        # api_instance = CreateNewWebhooksApi(config)
        # response, status, body = api_instance.create_webhook_subscription(create_webhook_request=request_body)

        print(f"\nWebhook Creation Status: {status}")
        print(f"Response Body: {body}")

        if status == 201:
            print("Successfully created wallet webhook!")
            print(f"JWT Secret: {response.security_policy.configuration.jwt_key}")

        return response

    except Exception as e:
        print(f"\nError creating webhook: {str(e)}")
        if hasattr(e, 'body'):
            print(f"Error details: {e.body}")
        return None

def clean_request(data):
    """Remove None values from request body"""
    if isinstance(data, dict):
        return {k: clean_request(v) for k, v in data.items() if v is not None}
    if isinstance(data, list):
        return [clean_request(item) for item in data]
    return data
