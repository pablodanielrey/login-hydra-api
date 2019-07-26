import uuid
import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, func, or_
from sqlalchemy.orm import relationship

from login.hydra.model.entities import Base

def generateId():
    return str(uuid.uuid4())


class ChallengeLog(Base):

    __tablename__ = 'challenge_log'

    id = Column(String, primary_key=True, default=generateId)
    created = Column(DateTime())

    client_id = Column(String())
    client_url = Column(String())
    client_name = Column(String())

    user_id = Column(String())
    username = Column(String())
    
    skip = Column(Boolean())

    data = Column(String())
