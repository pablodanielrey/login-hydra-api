
import logging
import datetime
from dateutil.parser import parse
import base64
import io

from flask import Blueprint, jsonify, request, send_file, make_response

from hydra.api.rest.models import hydraModel, hydraLocalModel, loginModel, qrModel
from hydra.model import open_session

bp = Blueprint('login', __name__, url_prefix='/login/api/v1.0')

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
            ch = hydraLocalModel.get_login_challenge(session, challenge)
            if not ch:
                status = 404
                return jsonify({'status':status, 'response':'Not found'}), status

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
    """
        La app cliente accede para verificar los datos del challenge y si tiene que saltar la autentificación o no.
        respuestas:
            200 - todo ok - con skip = True en el caso de tener que saltar la autentificación
            404 - (Not Found) - no se encuentra el challenge

    """
    try:
        assert challenge is not None

        data = request.json
        assert data['device_hash'] is not None

        device_hash = data['device_hash']
        ''' aca podría realizar cosas como rate limiting '''

        status, data = hydraModel.get_login_challenge(challenge)
        if status != 200:
            return jsonify({'status': 404, 'response': 'No encontrado'}), 404

        with open_session() as session:
            ch = hydraLocalModel.get_login_challenge(session, challenge)
            if not ch:
                hydraLocalModel.store_login_challenge(session, data)
                session.commit() 

        response = {
            'challenge': data['challenge'],
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
            hydraLocalModel.store_consent_challenge(session, data)
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


@bp.route('/device', methods=['POST'])
def get_device_id():
    try:
        data = request.json
        logging.info(data)

        with open_session() as session:
            hash_ = loginModel.generate_device(session, data['app_version'], data)
            session.commit()

        response = {
            'device_hash': hash_
        }
        return jsonify({'status': 200, 'response': response}), 200

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500

