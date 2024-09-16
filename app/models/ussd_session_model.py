import json
from configs.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text

class USSDSession(Base):
    __tablename__ = "ussd_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    phone_number = Column(String(15), index=True)
    state = Column(String(255))
    data = Column(Text)
    # TODO: add sessison creating and updating date


def get_session(db: Session, session_id: str):
    return db.query(USSDSession).filter(USSDSession.session_id == session_id).first()

def create_session(db: Session, session_id: str, phone_number: str, state: str, data: dict):
    db_session = USSDSession(
        session_id=session_id,
        phone_number=phone_number,
        state=state,
        data=json.dumps(data)
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(db: Session, session_id: str, state: str, data: dict):
    session = get_session(db, session_id)
    if session:
        session.state = state
        session.data = json.dumps(data)
        db.commit()
        db.refresh(session)
    return session

def delete_session(db: Session, session_id: str):
    session = get_session(db, session_id)
    if session:
        db.delete(session)
        db.commit()