
import logging
import datetime
from dateutil.parser import parse
import base64
import io

from flask import Blueprint, jsonify, request, send_file

from login.hydra.api.rest.models import hydraModel, logModel
from login.hydra.model import open_session

bp = Blueprint('users', __name__, url_prefix='/login/api/v1.0')

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json

        user = data['user']
        assert user is not None

        password = data['password']
        assert password is not None

        challenge = data['challenge']
        assert challenge is not None

        status, data = hydraModel.accept_login_challenge(challenge, 'sadsadasd', remember=False)
        if status != 200:
            raise Exception(data)   

        response = {
            'redirect_to': data['redirect_to']
        }

        return jsonify({'status': 200, 'response': response})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})


@bp.route('/challenge/<challenge>', methods=['GET'])
def get_challenge(challenge:str):
    try:
        assert challenge is not None

        status, data = hydraModel.get_login_challenge(challenge)
        if status != 200:
            raise Exception(data)

        with open_session() as session:
            logModel.log_challenge(session, data)
            session.commit() 

        response = {
            'challenge': challenge,
            'skip': data['skip']
        }
        return jsonify({'status': 200, 'response': response})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})


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

        return jsonify({'status': 200, 'response': response})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})







@bp.route('/challenges', methods=['GET'])
def get_all_challenges():
    try:
        import json
        with open_session() as session:
            challenges = logModel.get_log_challenges(session)
        return jsonify({'status': 200, 'response': challenges})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})

@bp.route('/consent_challenges', methods=['GET'])
def get_all_consent_challenges():
    try:
        import json
        with open_session() as session:
            challenges = logModel.get_consent_challenges(session)
        return jsonify({'status': 200, 'response': challenges})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})




@bp.route('/device/<did>', methods=['GET'])
def get_device_id(did:str):
    try:
        logging.info(did)
        return jsonify({'status': 200, 'response': 'cvxv'})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})

