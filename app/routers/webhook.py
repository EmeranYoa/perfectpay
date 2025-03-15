import logging
from fastapi import APIRouter, Depends, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Webhook"],
    responses={404: {"description": "Not found"}},
)

@router.post("/webhook")
async def webhook(request: Request):
  """ Webhook for CyberSource handler """
  logger.info("Received webhook")
  logger.info(request.json())
  # Verify JWT signature
  # Process payment status
  # Update wallet balance
  # Return 200 OK
  return {"status": "success"}


@router.get("/webhook-healthcheck")
async def webhook_healthcheck(request: Request):
  return {"status": "success"}
