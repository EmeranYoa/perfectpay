from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configs.config import settings
from app.configs.database import Base, engine, SessionLocal
from app.routers import auth, account, transaction, merchant, recharge, ussd
from fastapi_pagination import add_pagination

from app.models.fixtures import create_fixtures

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def connect():
    Base.metadata.create_all(bind=engine)

    create_fixtures(SessionLocal())


app.include_router(auth.router)
app.include_router(account.router)
app.include_router(merchant.router)
app.include_router(transaction.router)
app.include_router(recharge.router)
app.include_router(ussd.router)
