
import logging
import datetime
from dateutil.parser import parse
import base64
import io

from flask import Blueprint, request, jsonify, send_file

#from login.api.rest.models import usersModel

bp = Blueprint('users', __name__, url_prefix='/login/api/v1.0')

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        logging.info(data)

        return jsonify({'status': 200, 'response': 'ok'})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})


@bp.route('/device/<did>', methods=['GET'])
def get_device_id(did:str):
    try:
        logging.info(did)
        return jsonify({'status': 200, 'response': 'cvxv'})

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)})

