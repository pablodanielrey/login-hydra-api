
import logging
import json
import datetime
from dateutil.parser import parse
import base64
import io

from flask import Blueprint, jsonify, request, send_file, make_response

from hydra.api.rest.models import hydraModel, hydraLocalModel, loginModel, usersModel
from hydra.model import open_session
import users.model

bp = Blueprint('login', __name__, url_prefix='/login/api/v1.0')


"""
    Paso 1 - se obtiene un hash para el dispositivo que se encuentra accediendo al login.
    este hash se usa para todos los otras apis. (es solo informativo ya que puede ser hackeado facilmente)
"""

@bp.route('/device', methods=['POST'])
def get_device_id():
    '''
        Se obtiene un hash para el dispositivo. Se usa en todos las otras apis de login
        respuestas:
            200 - ok
            500 - error irrecuperable
    '''
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


"""
    Paso 2 - Se verifica que el challenge exista y si hay que saltar la autentificación
"""
@bp.route('/challenge/<challenge>', methods=['POST'])
def get_challenge(challenge:str):
    """
        La app cliente accede para verificar los datos del challenge y si tiene que saltar la autentificación o no.
        respuestas:
            200 - todo ok - con skip = True en el caso de tener que saltar la autentificación
            404 - (Not Found) - no se encuentra el challenge | error en hydra
            409 - (Gone) - el challenge ya fue usado
            500 - error del servidor

    """
    try:
        assert challenge is not None

        data = request.json
        assert data['device_hash'] is not None

        device_hash = data['device_hash']
        ''' aca podría realizar cosas como rate limiting '''

        status, data = hydraModel.get_login_challenge(challenge)
        if status == 409:
            return jsonify({'status': 409, 'response': {'error':'Ya usado'}}), 409
        if status != 200:
            return jsonify({'status': 404, 'response': {'error':'No encontrado'}}), 404

        ch = None
        try:
            with open_session() as session:
                ch = hydraLocalModel.get_login_challenge(session, challenge)
                if not ch:
                    hydraLocalModel.store_login_challenge(session, data)
                    session.commit()
                    ch = hydraLocalModel.get_login_challenge(session, challenge)

        except Exception as e1:
            response = {
                'redirect_to': data['request_url'],
                'error': str(e1)
            }
            return jsonify({'status': 500, 'response': response}), 500
        
        if data['skip']:
            ''' si skip == True entonces hay que aceptar|denegar el challenge en hydra '''
            uid = ch.user_id
            status, data = hydraModel.accept_login_challenge(challenge, device_hash, uid, remember=False)
            if status == 409:
                ''' 
                    El challenge ya fue usado, asi que se redirige a oauth nuevamente para regenerar otro.
                    en este paso no debería pasar nunca!!!
                '''
                redirect = ch.request_url
            if status != 200:
                ''' aca se trata de un error irrecuperable, asi que se reidrecciona el cliente hacia la url original de inicio de oauth '''
                redirect = ch.request_url

            response = {
                'challenge': ch.challenge,
                'skip': True,
                'redirect_to': redirect
            }
            return jsonify({'status':status, 'response':response}), status

        else:
            response = {
                'challenge': ch.challenge,
                'skip': False
            }
            return jsonify({'status': 200, 'response': response}), 200

    except Exception as e:
        response = {
            'error': str(e)
        }        
        return jsonify({'status': 500, 'response':response}), 500


"""
    Paso 3 - el usuario se loguea usando credenciales.
"""
def _get_user_email(user):
    for m in [m for m in user.mails if m.eliminado is None]:
        if m.confirmado:
            return m.email
    return None

@bp.route('/login', methods=['POST'])
def login():
    """
        Logueo de un usuario mediante credenciales de usuario y clave.
        Respuestas:
            200 - ok
            500 - excepción irrecuperable
            400 - (Bad request) - challenge no encontrado
            404 - (Not Found) - Usuario/clave no válidas
            409 - (Gone) - challenge que existía pero ya fue usado
    """
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

        position = data['position'] if 'position' in data else None

        usr = None
        with open_session() as session:
            ch = hydraLocalModel.get_login_challenge(session, challenge)
            if not ch:
                status = 400
                return jsonify({'status':status, 'response':{'error':'challenge not found'}}), status

            original_url = ch.request_url

            try:
                usr, hash_ = loginModel.login(session, user, password, device_id, challenge, position=position)
                session.commit()

                if usr:
                    d = hydraModel.get_device_logins(session, device_id)
                    d.success = d.success + 1
                    session.commit()

                    # aca se debe obtener el usuario para poder setearlo dentro del idtoken
                    uid = usr.usuario_id
                    with users.model.open_session() as users_session:
                        user = usersModel.get_user(users_session, uid)
                        if not user:
                            raise Exception(f'no se pudo obtener usuario con uid : {uid}')
       
                        context = {
                            'sub':user.id, 
                            'given_name': user.nombre,
                            'family_name': user.apellido,
                            'preferred_username': user.dni                            
                        }
                        mail_context = _get_user_email(user)
                        if mail_context:
                            context['email'] = mail_context
                            context['email_verified'] = True

                    status, data = hydraModel.accept_login_challenge(challenge=challenge, uid=uid, data=context, remember=False)
                    if status == 409:
                        ''' el challenge ya fue usado, asi que se redirige a oauth nuevamente para regenerar otro '''
                        redirect = ch.request_url
                    if status != 200:
                        ''' aca se trata de un error irrecuperable, asi que se reidrecciona el cliente hacia la url original de inicio de oauth '''
                        redirect = original_url
                    else:
                        redirect = data['redirect_to']

                    response = {
                        'hash': hash_,
                        'redirect_to': redirect
                    }
                    return jsonify({'status':status, 'response':response}), status

                else:
                    d = hydraModel.get_device_logins(session, device_id)
                    d.errors = d.errors + 1
                    session.commit()
        
                    status, data = hydraModel.deny_login_challenge(challenge, device_id, 'Credenciales incorrectas')
                    if status != 200:
                        ''' aca se trata de un error irrecuperable, asi que se reidrecciona el cliente hacia la url original de inicio de oauth '''
                        redirect = original_url
                    else:
                        redirect = data['redirect_to']
            
                    ''' seteo el codigo de error para 404 - debido a que las credenciales son incorrectas '''
                    status = 404
                    response = {
                        'hash': hash_,
                        'redirect_to': redirect
                    }
                    return jsonify({'status':status, 'response':response}), status

            except Exception as e1:
                response = {
                    'hash': None,
                    'redirect_to': original_url,
                    'error': str(e1)
                }
                return jsonify({'status': 500, 'response':response}), 500
                    
    except Exception as e:
        return jsonify({'status': 500, 'response':{'error':str(e)}}), 500


"""
    Paso 3 - Se acepta implícitamente el acceso a los datos del login por parte de la app cliente.
"""
@bp.route('/consent/<challenge>', methods=['GET'])
def get_consent_challenge(challenge:str):
    """
        Acepta el consentimiento del usuario para el acceso a los datos de la app cliente.
        respuestas:
            200 - ok

    """
    try:
        assert challenge is not None

        status, data = hydraModel.get_consent_challenge(challenge)
        if status != 200:
            raise Exception(data)

        original_url = data['request_url']

        try:
            with open_session() as session:
                hydraLocalModel.store_consent_challenge(session, data)
                session.commit()

            scopes = data['requested_scope']
            context = data['context']
            status, redirect = hydraModel.accept_consent_challenge(challenge=challenge, scopes=scopes, context=context, remember=False)
            if status != 200:
                response = {
                    'redirect_to': original_url
                }
                return jsonify({'status': status, 'response':response}), status
            else:
                response = {
                    'skip': data['skip'],
                    'scopes': data['requested_scope'],
                    'audience': data['requested_access_token_audience'],
                    'subject': data['subject'],
                    'redirect_to': redirect['redirect_to']
                }
                return jsonify({'status': 200, 'response': response}), 200

        except Exception as e1:
            response = {
                'error': str(e1),
                'redirect_to': original_url
            }
            return jsonify({'status': 500, 'response':response}), 500

    except Exception as e:
        return jsonify({'status': 500, 'response':{'error':str(e)}}), 500

