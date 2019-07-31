
import datetime
import os
import pyqrcode

from .entities.QR import QrCode

class QRModel:

    def generate_qr(self, session, seed:str, challenge:str) -> str:
        seed2 = os.urandom(5).hex()
        code = f"{seed2}{seed}"

        qr = QrCode()
        qr.created = datetime.datetime.utcnow()
        qr.code = code
        qr.challenge = challenge
        session.add(qr)
       
        url = f'http://login:10005/login/qrcode/activar/{code}'

        cqr = pyqrcode.create(url).png_as_base64_str(scale=3)
        return code, cqr

    def verify_qr(self, session, code:str) -> bool:
        q = session.query(QrCode).filter(QrCode.code == code).count()
        return q == 1

    def get_qr_code(self, session, code:str) -> QrCode:
        q = session.query(QrCode).filter(QrCode.code == code).one()
        return q