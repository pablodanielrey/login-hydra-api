import uuid
import datetime
import json

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, func, or_
from sqlalchemy.orm import relationship

from hydra.model.entities import Base

def generateId():
    return str(uuid.uuid4())


class DeviceLogins(Base):

    __tablename__ = 'device_logins'

    id = Column(String, primary_key=True, default=generateId)
    created = Column(DateTime())

    device_id = Column(String())
    errors = Column(Integer(), default=0)
    success = Column(Integer(), default=0)


class ChallengeLog(Base):

    __tablename__ = 'challenge_log'

    id = Column(String, primary_key=True, default=generateId)
    created = Column(DateTime())

    challenge = Column(String())

    client_id = Column(String())
    client_url = Column(String())
    client_name = Column(String())

    user_id = Column(String())
    username = Column(String())
    
    skip = Column(Boolean())

    data = Column(String())


class ConsentChallengeLog(Base):

    __tablename__ = 'challenge_consent'

    id = Column(String, primary_key=True, default=generateId)
    created = Column(DateTime())

    challenge = Column(String())

    client_id = Column(String())
    client_url = Column(String())
    client_name = Column(String())

    user_id = Column(String())
    username = Column(String())
    
    skip = Column(Boolean())

    login_session_id = Column(String())
    login_challenge = Column(String())

    data = Column(String())
