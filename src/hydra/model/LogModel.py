
import json
import datetime

from .entities.Hydra import ChallengeLog, ConsentChallengeLog

class LogModel:

    def log_challenge(self, session, challenge):
        c = ChallengeLog()
        c.created = datetime.datetime.utcnow()
        c.challenge = challenge['challenge']
        c.client_id = challenge['client']['client_id']
        c.client_name = challenge['client']['client_name']
        c.client_url = challenge['client']['client_uri']
        c.username = ''
        c.user_id = challenge['subject']
        c.skip = challenge['skip']
        c.data = json.dumps(challenge)
        session.add(c)

    def log_consent_challenge(self, session, challenge):
        c = ConsentChallengeLog()
        c.created = datetime.datetime.utcnow()
        c.challenge = challenge['challenge']
        c.client_id = challenge['client']['client_id']
        c.client_name = challenge['client']['client_name']
        c.client_url = challenge['client']['client_uri']
        c.username = ''
        c.user_id = challenge['subject']
        c.skip = challenge['skip']
        c.login_challenge = challenge['login_challenge']
        c.login_session_id = challenge['login_session_id']
        c.data = json.dumps(challenge)
        session.add(c)

    def get_log_challenges(self, session):
        q = session.query(ChallengeLog).order_by(ChallengeLog.created.desc()).all()
        return q

    def get_log_challenge(self, session, challenge):
        q = session.query(ChallengeLog).filter(ChallengeLog.challenge == challenge).one()
        return q

    def get_consent_challenges(self, session):
        q = session.query(ConsentChallengeLog).order_by(ConsentChallengeLog.created.desc()).all()
        return q
