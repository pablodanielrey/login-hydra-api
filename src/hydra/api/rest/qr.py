import logging
import datetime
from dateutil.parser import parse
import base64
import io
import pyqrcode

from flask import Blueprint, jsonify, request, send_file, make_response

from hydra.api.rest.models import hydraModel, hydraLocalModel, loginModel, qrModel
from hydra.model import open_session

bp = Blueprint('qr', __name__, url_prefix='/login/api/v1.0')

@bp.route('/qrcode/<device_hash>', methods=['POST'])
def generate_qr_code(device_hash):
    """
        La app cliente accede para generar un nuevo qr de autentificación para ser escaneado.
        respuestas:
            404 - (Not Found) dispositivo o challenge no encontrados
            400 - (Bad Request) la url no está en las registradas para el cliente
            200 - código qr y datauri
            429 - (no implemetnada todavía) para rate-limiting
    """
    try:
        assert device_hash is not None

        data = request.json

        challenge = data['challenge']
        assert challenge is not None

        redirect_to_accept = data['redirect']
        assert redirect_to_accept is not None

        with open_session() as session:
            d = loginModel.get_device_by_hash(session, device_hash)
            if not d:
                return jsonify({'status':404, 'response':f'Dispositivo {device_hash} no existente'}), 404

            ''' TODO: aca puedo generar chequeos para evitar DOS '''
            """
                if muchas peticiones:
                return jsonify({'status':429, 'response':'demasiadas peticiones'}), 429    
            """

            ''' verifico el challenge '''
            ch = hydraLocalModel.get_login_challenge(session, challenge)
            if not ch:
                return jsonify({'status':404, 'response':f'Challenge {challenge} no existente'}), 404

            ''' verifico que la redirección enviada por el cliente se encuentre dentro de las registradas '''
            redirects = ch.client_redirects
            all_redirects = redirects.split(',')
            for r_ in all_redirects:
                if r_.split('/')[0] in redirect_to_accept:
                    break
            else:
                return jsonify({'status':400, 'response':f'{redirect_to_accept} no se encuentra registrado para el cliente'}), 400
                

            ''' genero el código qr '''
            code = qrModel.generate_qr(session, d.id, challenge, redirect_to_accept)
            session.commit()

            url = f'{redirect_to_accept}/{code}'
            cqr = pyqrcode.create(url).png_as_base64_str(scale=3)
            datauri = f"data:image/png;base64,{cqr}"

            response = {
                'code': code,
                'qr_datauri': datauri
            }

        return jsonify({'status':200, 'response':response}), 200
       
    except Exception as e:
        response = {
            'error': str(e)
        }
        return jsonify({'status': 500, 'response':response}), 500


@bp.route('/login_qrcode/<qr>', methods=['GET'])
def get_login_hash(qr):
    """
        Lo accede el cliente que está tratando de ingresar al sistema (donde se muestra el código qr).
        respuesta:
            200 --> qr aceptado
            304 --> (Not Modified) - qr pendiente
            404 --> (Not Found) - qr no existente
            410 --> (Gone) - qr ya usado
    """
    try:
        with open_session() as session:
            qr = qrModel.get_qr_code(session, qr)
            if qr.used:
                return jsonify({'status': 410, 'response':'Qr ya usado'}), 410

            if qr.activated == True:
                qr.used = datetime.datetime.utcnow()
                session.commit()
                response = {
                    'redirect_to': qr.redirect
                }
                return jsonify({'status': 200, 'response':response}), 200
            else:
                response = {
                    'retry_in': 10
                }
                return jsonify({'status': 304, 'response':response}), 304

    except Exception as e:
        return jsonify({'status': 404, 'response':'Not Found'}), 404


@bp.route('/login_qrcode/<qr>', methods=['POST'])
def login_hash(qr):
    try:
        assert qr is not None

        data = request.json

        hash_ = data['hash']
        assert hash_ is not None

        device_id = data['device_id']
        assert device_id is not None

        with open_session() as session:
            ''' verifico que el qr exista y haya sido generado '''
            qr = qrModel.get_qr_code(session, qr)
            if not qr:
                status = 404
                return jsonify({'status':status, 'response':'Not found'}), status

            ''' verifico que el challenge exista '''
            ch = hydraLocalModel.get_login_challenge(session, qr.challenge)
            if not ch:
                status = 404
                return jsonify({'status':status, 'response':'Not found'}), status                

            if not qr.activated:
                challenge = qr.challenge
                h = loginModel.login_hash(session, hash_, device_id, challenge)
                status, resp = hydraModel.process_user_login(session, device_id, challenge, h.user_id if h else None)
                qr.redirect = resp['redirect_to']
                qr.activated = True
                session.commit()
            else:
                ''' TODO: ver si esto esta ok '''
                status = 304
                return jsonify({'status':status, 'response':'Not Modified'}), status

            response = {
                'code': qr,
                'updated': True
            }

            return jsonify({'status':status, 'response':response}), status
       
    except Exception as e:
        ''' TODO: ver si se puede obtener la url del cliente original del pedido y redireccionar ahi para que se vuelva a intentar todo el flujo de auth '''
        response = {
            'redirect_to': '/',
            'error': str(e)
        }
        return jsonify({'status': 500, 'response':response}), 500
