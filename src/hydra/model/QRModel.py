
import datetime
import os

from .entities.QR import QrCode

class QRModel:

    def generate_qr(self, session, device_id:str, challenge:str, redirect_to_accept:str) -> str:
        code = os.urandom(10).hex()
        while session.query(QrCode).filter(QrCode.code == code).count() > 0:
            code = os.urandom(10).hex()

        qr = QrCode()
        qr.created = datetime.datetime.utcnow()
        qr.code = code
        qr.challenge = challenge
        qr.redirect_to_accept = redirect_to_accept
        qr.device_id = device_id
        session.add(qr)
       
        return code

    def verify_qr(self, session, code:str) -> bool:
        q = session.query(QrCode).filter(QrCode.code == code).count()
        return q == 1

    def get_qr_code(self, session, code:str) -> QrCode:
        q = session.query(QrCode).filter(QrCode.code == code).one()
        return q