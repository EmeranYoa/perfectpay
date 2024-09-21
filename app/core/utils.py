import random
from passlib.context import CryptContext


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