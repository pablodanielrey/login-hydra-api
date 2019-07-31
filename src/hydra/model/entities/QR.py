import uuid
import datetime
import json

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, func, or_
from sqlalchemy.orm import relationship

from hydra.model.entities import Base

def generateId():
    return str(uuid.uuid4())

class QrCode(Base):

    __tablename__ = 'qr_code'

    id = Column(String, primary_key=True, default=generateId)
    created = Column(DateTime())

    code = Column(String())
    challenge = Column(String())

    activated = Column(Boolean(), default=False)
    redirect = Column(String())

    used = Column(DateTime())