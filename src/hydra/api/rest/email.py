
import logging
import datetime
from dateutil.parser import parse
import base64
import io
import os

from flask import Blueprint, jsonify, request, send_file, make_response

from login.model import obtener_session as login_open_session
from users.model import open_session as users_open_session

from hydra.api.rest.models import hydraModel, hydraLocalModel, loginModel, usersModel
from hydra.model import open_session

INTERNAL_DOMAINS = os.environ['INTERNAL_DOMAINS'].split(',')

bp = Blueprint('email', __name__, url_prefix='/email/api/v1.0')


@bp.route('/analize/<challenge>', methods=['POST'])
def analize(challenge):
    try:
        data = request.json
        """
        assert data and 'device' in data and data['device'] is not None
        assert data and 'email' in data and data['email'] is not None
        assert data and 'user' in data and data['user'] is not None
        """

        #device = data['device']

        ch = hydraModel.get_consent_challenge(challenge)

        response = {
            "configure": True,
            "challenge": challenge,
            "redirect_to": ""
        }

        response = {
            'status': 200,
            'response': response
        }
        return jsonify(response), 200

        """
        with users_open_session() as user_session:
            with open_session() as recover_session:
                try:
                    model = RecoverModel(recover_session, user_session, loginModel, mailsModel, INTERNAL_DOMAINS, RESET_FROM)
                    r = model.recover_for(user, device)
                    recover_session.commit()

                    response = {
                        'status': 200,
                        'response': r
                    }
                    return jsonify(response), 200

                except Exception as e:
                    recover_session.rollback()
                    response = {
                        'status': 400,
                        'response': str(e)
                    }
                    return jsonify(response), 200
"""
    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500


@bp.route('/configure', methods=['POST'])
def recover_for():
    try:
        data = request.json
        assert data and 'device' in data and data['device'] is not None
        assert data and 'email' in data and data['email'] is not None
        assert data and 'challenge' in data and data['challenge'] is not None

        device = data['device']
        challenge = data['challenge']

        ch = hydraModel.get_consent_challenge(challenge)

        """
            Se genera un registro de confirmación de correo alternativo.
        """ 
        rid = 'asdsadsasdasdsdsad'
        response = {
            'status': 200,
            'response': rid
        }
        return jsonify(response), 200

        """
        with users_open_session() as user_session:
            with open_session() as recover_session:
                try:
                    model = RecoverModel(recover_session, user_session, loginModel, mailsModel, INTERNAL_DOMAINS, RESET_FROM)
                    r = model.recover_for(user, device)
                    recover_session.commit()

                    response = {
                        'status': 200,
                        'response': r
                    }
                    return jsonify(response), 200

                except Exception as e:
                    recover_session.rollback()
                    response = {
                        'status': 400,
                        'response': str(e)
                    }
                    return jsonify(response), 200
"""
    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500


@bp.route('/verify_code/<code>', methods=['POST'])
def verify_code(code):
    try:
        data = request.json
        assert data and 'challenge' in data and data['challenge'] is not None
        assert data and 'device' in data and data['device'] is not None
        assert data and 'eid' in data and data['eid'] is not None

        challenge = data['challenge']

        response = {
            'verified':True,
            'challenge': challenge 
        }

        response = {
            'status': 200,
            'response': response
        }
        return jsonify(response), 200


        """
        user = data['user']

        with users_open_session() as user_session:
            with open_session() as recover_session:
                try:
                    model = RecoverModel(recover_session, user_session, loginModel, mailsModel, INTERNAL_DOMAINS, RESET_FROM)
                    r = model.verify_code(user, code)
                    recover_session.commit()

                    response = {
                        'status': 200,
                        'response': {
                            'session':r
                        }
                    }
                    return jsonify(response), 200

                except Exception as e:
                    recover_session.rollback()
                    response = {
                        'status': 400,
                        'response': str(e)
                    }
                    return jsonify(response), 200        

        """

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500
