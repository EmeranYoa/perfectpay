from typing import Union
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles

from app.configs.config import settings, babel, babel_configs
from app.configs.database import Base, engine, SessionLocal
from app.routers import auth, account, transaction, merchant, recharge, ussd, webhook
from fastapi_pagination import add_pagination
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.tasks import update_currency_rates

from fastapi_babel import BabelMiddleware, _

scheduler = BackgroundScheduler()

class LocaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        lang = request.query_params.get("lang", "en")
        babel.locale = lang

        response = await call_next(request)
        return response

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="PerfectPay API",
    contact={
        "name": "Hamed Nsangou & Emeran Youa",
        "email": "emeran.yoa@gmail.com",
    },
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

add_pagination(app)

origins = ['*']

# mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BabelMiddleware, babel_configs=babel_configs)
app.add_middleware(LocaleMiddleware)

@app.on_event("startup")
async def connect():
    # scheduler.add_job(create_fixtures, 'interval', seconds=10, args=[SessionLocal()])
    # scheduler.add_job(
    #     func=update_currency_rates,
    #     trigger="interval",
    #     seconds=10,
    #     args=[SessionLocal()]
    # )

    scheduler.add_job(
        func=update_currency_rates,
        trigger=CronTrigger(hour=6, minute=0),  # Every day at 6:00 AM
        args=[SessionLocal()]
    )

    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()

app.include_router(auth.router)
app.include_router(account.router)
app.include_router(merchant.router)
app.include_router(transaction.router)
app.include_router(recharge.router)
app.include_router(ussd.router)
app.include_router(webhook.router)
