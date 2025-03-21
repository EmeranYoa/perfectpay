import json
from datetime import timedelta, datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, Session as Db_session
from sqlalchemy.sql import func

from app.configs.database import Base
from app.schemas.session_schema import SessionCreate, SessionUpdate


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    last_activity = Column(DateTime, server_default=func.now(), onupdate=func.now())
    state = Column(String(255))
    data = Column(Text)
    expiration = Column(DateTime, nullable=False)  # Timestamp for session expiration

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="sessions", foreign_keys=[user_id])


def get_session(db: Db_session, session_id: str):
    return db.query(Session).filter(Session.session_id == session_id).first()

def create_session(db: Db_session, session: SessionCreate):
    db_session = Session(
        session_id=session.session_id,
        user_id=session.user_id,
        state=session.state,
        data=json.dumps(session.data),
        expiration=datetime.now() + timedelta(minutes=1)  # Session expires in 1 minutes
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(db: Db_session, session: SessionUpdate):
    db_session = get_session(db, session.session_id)
    if db_session:
        db_session.state = session.state
        db_session.data = json.dumps(session.data)
        db.commit()
        db.refresh(db_session)
    return db_session

def delete_session(db: Db_session, session_id: str):
    session = get_session(db, session_id)
    if session:
        db.delete(session)
        db.commit()