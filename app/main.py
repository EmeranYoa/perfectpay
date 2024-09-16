from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.config import settings
from configs.database import Base, engine
from routers import payin, credit_card, client, ussd


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Perfect Pay API",
    contact={
        "name": "Emeran Youa",
        "email": "emeran.yoa@gmail.com",
    },
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
)

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


app.include_router(payin.router)
app.include_router(credit_card.router)
app.include_router(client.router)
app.include_router(ussd.router)