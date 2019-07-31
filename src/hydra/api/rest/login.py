
import logging
import datetime
from dateutil.parser import parse
import base64
import io

from flask import Blueprint, jsonify, request, send_file, make_response

from hydra.api.rest.models import hydraModel, logModel, loginModel, qrModel
from hydra.model import open_session

bp = Blueprint('users', __name__, url_prefix='/login/api/v1.0')


@bp.route('/qrcode/<device_hash>', methods=['POST'])
def get_qr_code(device_hash):
    try:
        assert device_hash is not None

        data = request.json
        challenge = data['challenge']
        assert challenge is not None

        with open_session() as session:
            d = loginModel.get_device_by_hash(session, device_hash)
            ''' TODO: aca puedo generar chequeos para evitar DOS '''

            seed = d.id
            code, qr = qrModel.generate_qr(session, seed, challenge)
            session.commit()

            uri = datauri = f"data:image/png;base64,{qr}"

            response = {
                'code': code,
                'qr_datauri': uri
            }

        return jsonify({'status':200, 'response':response}), 200
       
    except Exception as e:
        response = {
            'error': str(e)
        }
        return jsonify({'status': 500, 'response':response}), 500


@bp.route('/login/<qr>', methods=['GET'])
def get_login_hash(qr):
    try:
        with open_session() as session:
            qr = qrModel.get_qr_code(session, qr)
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
                return jsonify({'status': 202, 'response':response}), 200

    except Exception as e:
        return jsonify({'status': 404, 'response':'Not Found'}), 404


@bp.route('/login/<qr>', methods=['POST'])
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

            if not qr.activated:
                challenge = qr.challenge
                h = loginModel.login_hash(session, hash_, device_id, challenge)
                status, resp = hydraModel.process_user_login(session, device_id, challenge, h.user_id if h else None)
                qr.redirect = resp['redirect_to']
                qr.activated = True
                session.commit()

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



@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json

        user = data['user']
        assert user is not None

        password = data['password']
        assert password is not None

        device_id = data['device_id']
        assert device_id is not None

        challenge = data['challenge']
        assert challenge is not None

        usr = None
        with open_session() as session:
            log_challenge = logModel.get_log_challenge(session, challenge)

            usr, hash_ = loginModel.login(session, user, password, device_id, challenge)
            session.commit()

            status, resp = hydraModel.process_user_login(session, device_id, challenge, usr.usuario_id if usr else None)
            session.commit()

            response = {
                'hash': hash_,
                'redirect_to': resp['redirect_to']
            }

            return jsonify({'status':status, 'response':response}), status
       
    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500


@bp.route('/challenge/<challenge>', methods=['POST'])
def get_challenge(challenge:str):
    try:
        assert challenge is not None
        data = request.json
        assert data['device_id'] is not None

        status, data = hydraModel.get_login_challenge(challenge)
        if status == 404 or status == 409:
            return jsonify({'status': 404, 'response': 'Inválido'}), 404
        if status != 200:
            raise Exception(data)

        with open_session() as session:
            logModel.log_challenge(session, data)
            session.commit() 

        response = {
            'challenge': challenge,
            'skip': data['skip']
        }
        return jsonify({'status': 200, 'response': response}), 200

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500


@bp.route('/consent/<challenge>', methods=['GET'])
def get_consent_challenge(challenge:str):
    try:
        assert challenge is not None

        status, data = hydraModel.get_consent_challenge(challenge)
        if status != 200:
            raise Exception(data)

        with open_session() as session:
            logModel.log_consent_challenge(session, data)
            session.commit()

        scopes = data['requested_scope']
        status, redirect = hydraModel.accept_consent_challenge(challenge, scopes, remember=False)
        if status != 200:
            raise Exception(data)

        response = {
            'skip': data['skip'],
            'scopes': data['requested_scope'],
            'audience': data['requested_access_token_audience'],
            'subject': data['subject'],
            'redirect_to': redirect['redirect_to']
        }

        return jsonify({'status': 200, 'response': response}), 200

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500


@bp.route('/challenges', methods=['GET'])
def get_all_challenges():
    try:
        import json
        with open_session() as session:
            challenges = logModel.get_log_challenges(session)
        return jsonify({'status': 200, 'response': challenges}), 200

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500

@bp.route('/consent_challenges', methods=['GET'])
def get_all_consent_challenges():
    try:
        import json
        with open_session() as session:
            challenges = logModel.get_consent_challenges(session)
        return jsonify({'status': 200, 'response': challenges}), 200

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500



@bp.route('/device', methods=['POST'])
def get_device_id():
    try:
        data = request.json
        logging.info(data)

        with open_session() as session:
            hash_ = loginModel.generate_device(session, data['app_version'], data)
            session.commit()

        response = {
            'device_id': hash_
        }
        return jsonify({'status': 200, 'response': response}), 200

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500

