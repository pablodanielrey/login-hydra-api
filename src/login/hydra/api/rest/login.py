
import logging
import datetime
from dateutil.parser import parse
import base64
import io

from flask import Blueprint, request, jsonify, send_file

from login.hydra.api.rest.models import hydraModel, logModel
from login.hydra.model import open_session

bp = Blueprint('users', __name__, url_prefix='/login/api/v1.0')

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        logging.info(data)
        return jsonify({'status': 200, 'response': 'ok'})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})



@bp.route('/challenges', methods=['GET'])
def get_all_challenges():
    try:
        with open_session() as session:
            challenges = logModel.get_log_challenges(session)
        return jsonify({'status': 200, 'response': challenges})

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
            'skip': data['skip']
        }
        return jsonify({'status': 200, 'response': response})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})


@bp.route('/device/<did>', methods=['GET'])
def get_device_id(did:str):
    try:
        logging.info(did)
        return jsonify({'status': 200, 'response': 'cvxv'})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})

