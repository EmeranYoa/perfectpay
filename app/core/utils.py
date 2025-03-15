import random
from passlib.context import CryptContext
from PyCurrency_Converter import convert
from requests.exceptions import JSONDecodeError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def secure_pwd(raw_password):
    hashed = pwd_context.hash(raw_password)

    return hashed

def verify_pwd(plain, hash):
    return pwd_context.verify(plain, hash)


def generate_pin_code():
    return str(random.randint(10000, 99999))

def generate_merchant_code():
    return str(random.randint(100000, 999999))

def currency_rate_converter(from_currency, to_currency, amount=1):
    """
    Convert currency with fallback to default rates if API fails.
    """
    fallback_rates = {
        ("USD", "EUR"): 0.95,
        ("USD", "XAF"): 623.44,
        ("EUR", "USD"): 1.05,
        ("EUR", "XAF"): 656.32,
        ("XAF", "USD"): 0.0016,
        ("XAF", "EUR"): 0.0015,
    }

    try:
        converted_amount = convert(amount, from_currency, to_currency)
        print(f"Converted {amount} {from_currency} to {converted_amount} {to_currency}")
        return converted_amount
    except Exception as e:
        if (from_currency, to_currency) in fallback_rates:
            fallback_rate = fallback_rates[(from_currency, to_currency)]
            converted_amount = amount * fallback_rate
            print(f"Using fallback rate: {amount} {from_currency} = {converted_amount} {to_currency}")
            return converted_amount
        else:
            raise ValueError(f"No fallback rate available for {from_currency} to {to_currency}.")