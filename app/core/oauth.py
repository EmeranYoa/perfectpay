from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from configs.config import settings
from configs.database import get_db


from models.user_model import User
from core.utils import verify_pwd, secure_pwd

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        is_token_valid: bool = False
        try:
            payload = jwt.decode(jwtoken, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError as e:
            raise HTTPException(status_code=403, detail="Token has expired or invalid ")
        if payload:
            is_token_valid = True

        return is_token_valid

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def refresh_token(token: str):
    try:
        payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
   
        phone_number: str = payload.get("sub")
        expire = payload.get("exp")
        type = payload.get("type")

        if type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if expire is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        if phone_number is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        access = create_refresh_token(payload)
        refresh = create_refresh_token(payload)

        return {"access": access, "refresh": refresh}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
        token_data = {"phone_number": phone_number}
    except JWTError:
        raise credentials_exception
    return token_data


def jwt_decode(token:str):
    token_data = None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        phone_number: str = payload.get("sub")
        exp = payload.get('exp')
        token_data = {"phone_number": phone_number, "exp": exp}
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(token: str = Depends(JWTBearer()), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.phone_number == token_data["phone_number"]).first()
    if user is None:
        raise credentials_exception
    return user