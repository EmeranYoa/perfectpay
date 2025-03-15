
from app.core.utils import currency_rate_converter
from app.models.user_model import CurrencyRate
from sqlalchemy.orm import Session
from datetime import datetime

def update_currency_rates(db: Session):

    supported_currencies = ["USD", "EUR", "XAF"]
    # rate for 1 USD to 1 EUR

    for currency in supported_currencies:
        # currency to euro
        if currency == "USD":
            euro_rate = currency_rate_converter(currency, "EUR")
            xaf_rate = currency_rate_converter(currency, "XAF")
            currency_rate = db.query(CurrencyRate).filter(CurrencyRate.from_currency == currency, CurrencyRate.to_currency=="EUR").first()
            
            if currency_rate:
                currency_rate.rate = euro_rate
                currency_rate.updated_at = datetime.now()
                db.commit()
            else:
                currency_rate = CurrencyRate(from_currency=currency, to_currency="EUR", rate=euro_rate)
                db.add(currency_rate)
                db.commit()
            currency_rate = db.query(CurrencyRate).filter(CurrencyRate.from_currency == currency, CurrencyRate.to_currency=="XAF").first()
            if currency_rate:
                currency_rate.rate = xaf_rate
                currency_rate.updated_at = datetime.now()

                db.commit()
            else:
                currency_rate = CurrencyRate(from_currency=currency, to_currency="XAF", rate=xaf_rate)
                db.add(currency_rate)
                db.commit()
        elif currency == "EUR":
            usd_rate = currency_rate_converter(currency, "USD")
            xaf_rate = currency_rate_converter(currency, "XAF")
            currency_rate = db.query(CurrencyRate).filter(CurrencyRate.from_currency == currency, CurrencyRate.to_currency=="USD").first()
            
            if currency_rate:
                currency_rate.rate = usd_rate
                currency_rate.updated_at = datetime.now()
                db.commit()
            else:
                currency_rate = CurrencyRate(from_currency=currency, to_currency="USD", rate=usd_rate)
                db.add(currency_rate)
                db.commit()
            currency_rate = db.query(CurrencyRate).filter(CurrencyRate.from_currency == currency, CurrencyRate.to_currency=="XAF").first()
            if currency_rate:
                currency_rate.rate = xaf_rate
                currency_rate.updated_at = datetime.now()
                db.commit()
            else:
                currency_rate = CurrencyRate(from_currency=currency, to_currency="XAF", rate=xaf_rate)
                db.add(currency_rate)
                db.commit()
        else :
            euro_rate = currency_rate_converter(currency, "USD")
            euro_rate = currency_rate_converter(currency, "EUR")
            currency_rate = db.query(CurrencyRate).filter(CurrencyRate.from_currency == currency, CurrencyRate.to_currency=="USD").first()
            
            if currency_rate:
                currency_rate.rate = euro_rate
                currency_rate.updated_at = datetime.now()
                db.commit()
            else:
                currency_rate = CurrencyRate(from_currency=currency, to_currency="USD", rate=euro_rate)
                db.add(currency_rate)
                db.commit()
                
            currency_rate = db.query(CurrencyRate).filter(CurrencyRate.from_currency == currency, CurrencyRate.to_currency=="EUR").first()
            
            if currency_rate:
                currency_rate.rate = euro_rate
                currency_rate.updated_at = datetime.now()
                db.commit()
            else:
                currency_rate = CurrencyRate(from_currency=currency, to_currency="EUR", rate=euro_rate)
                db.add(currency_rate)
                db.commit()