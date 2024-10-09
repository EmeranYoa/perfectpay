import secrets
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Session
from app.configs.database import Base, get_db
from app.configs.config import api_key_header
from fastapi import Depends, Security, HTTPException
from datetime import datetime, timedelta

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expiration = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="api_keys", foreign_keys=[user_id])


def generate_api_key(user_id: int, db: Session):
    key = secrets.token_urlsafe(32)
    api_key = APIKey(
        key=key,
        user_id=user_id,
        active=True
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key.key

def get_api_key(
    api_key: str = Security(api_key_header), db: Session = Depends(get_db)
):
    key_in_db = db.query(APIKey).filter(APIKey.key == api_key, APIKey.active == True).first()
    if not key_in_db:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key_in_db.user_id  