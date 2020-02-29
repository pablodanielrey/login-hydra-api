
import logging
import datetime
from dateutil.parser import parse
import base64
import io
import os
import hashlib
import uuid


from flask import Blueprint, jsonify, request, send_file, make_response

from login.model import obtener_session as login_open_session
from users.model import open_session as users_open_session

from hydra.api.rest.models import hydraModel, hydraLocalModel, loginModel, usersModel
from hydra.model import open_session

"""
    TODO: HACK ASQUEROSOOO PARA SOLUCIONAR AHORA AGREGAR UN CORREO CONFIRMADO!!!
"""
from users.model.entities.User import Mail, MailTypes

INTERNAL_DOMAINS = os.environ['INTERNAL_DOMAINS'].split(',')
EMAIL_FROM = os.environ['EMAIL_FROM']
EMAILS_API_URL = os.environ['EMAILS_API_URL']

from hydra.model.MailsModel import MailsModel
mailsModel = MailsModel(EMAILS_API_URL)

bp = Blueprint('email', __name__, url_prefix='/email/api/v1.0')


@bp.route('/analize/<challenge>', methods=['POST'])
def analize(challenge):
    try:
        #data = request.json

        status, chdata = hydraModel.get_consent_challenge(challenge)
        if status != 200:
            raise Exception('error obteniendo los datos del challenge')

        """
            verifica si tiene email configurado en el contexto desde el login.
            en caso de no tenerlo hace falta configurar un correo.
        """
        configure = True
        if 'email' in chdata['context']:
            configure = False

        response = {
            "configure": configure,
            "challenge": challenge
        }

        response = {
            'status': 200,
            'response': response
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500


def _generate_code(ch, challenge, email):
    seed = ch['login_session_id'] + challenge + email
    hash_ = code = hashlib.sha256(seed.encode('utf-8')).hexdigest()
    code = hash_[-4:]
    return code

def _send_code_to(user, code, email):
    templ = mailsModel.get_template('code.tmpl')
    text = templ.render(user=user, code=code)
    r = mailsModel.send_email(EMAIL_FROM, email, 'Correo de contacto FCE', text)
    return r.ok

@bp.route('/configure', methods=['POST'])
def configure_email():
    try:
        data = request.json
        assert data and 'device' in data and data['device'] is not None
        assert data and 'email' in data and data['email'] is not None
        assert data and 'challenge' in data and data['challenge'] is not None

        #device = data['device']
        challenge = data['challenge']
        email = data['email']

        """
            chequeo que no sea alguno de los dominios internos.
        """
        email_domain = email.split('@')[1]
        if email_domain in INTERNAL_DOMAINS:
            raise Exception('Correo institucional no permitido')

        """ 
            genero un código determinista a apartir de los datos del challenge
            para no usar una entidad adicional en la base de datos.
        """
        status, ch = hydraModel.get_consent_challenge(challenge)
        if status != 200:
            raise Exception('error obteniendo el challenge')
        code = _generate_code(ch, challenge, email)

        user = {
            'firstname': ch['context']['given_name'],
            'lastname': ch['context']['family_name']
        }

        if not _send_code_to(user, code, email):
            raise Exception(f'no se pudo enviar el correo a {email}')

        response = {
            'status': 200,
            'response': 'walter_miguel_leo_jano_ivan_maxi_pablo'
        }
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'status': 500, 'response':str(e)}), 500


@bp.route('/verify_code/<code>', methods=['POST'])
def verify_code(code):
    try:
        data = request.json
        assert data and 'challenge' in data and data['challenge'] is not None
        assert data and 'device' in data and data['device'] is not None
        assert data and 'eid' in data and data['eid'] is not None
        assert data and 'email' in data and data['email'] is not None

        challenge = data['challenge']
        email = data['email']

        """ 
            genero un código determinista a apartir de los datos del challenge
            para no usar una entidad adicional en la base de datos.
        """        
        status, ch = hydraModel.get_consent_challenge(challenge)
        if status != 200:
            raise Exception('error obteniendo el challenge')

        user_id = ch['context']['sub']
        if not user_id:
            raise Exception('No se pudo obtener el usuario')

        code_to_verify = _generate_code(ch, challenge, email)
        verified = code == code_to_verify
        if verified:
            """
                registro el correo dentro del usuario como confirmado
            """
            """
                TODO: HACK ASQUEROSOOO PARA SOLUCIONAR AHORA AGREGAR UN CORREO CONFIRMADO!!!
                lo hao fuera del modelo, pero debe ir adentro.
            """
            from users.model.entities.User import Mail, MailTypes
            with users_open_session() as session:
                mail_ = Mail()
                mail_.id = str(uuid.uuid4())
                mail_.user_id = user_id
                mail_.confirmed = datetime.datetime.utcnow()
                mail_.email = email
                mail_.type = MailTypes.ALTERNATIVE
                session.add(mail_)
                session.commit()

        response = {
            'verified': verified,
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
