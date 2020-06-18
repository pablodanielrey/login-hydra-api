
import json
import datetime

from .entities.Hydra import LoginChallenge, ConsentChallenge

class HydraLocalModel:

    def get_challenge(self, challenge):
        c = LoginChallenge()
        c.created = datetime.datetime.utcnow()
        c.challenge = challenge['challenge']
        c.client_id = challenge['client']['client_id']
        c.client_name = challenge['client']['client_name']
        c.client_url = challenge['client']['client_uri']
        c.client_redirects = challenge['client']['redirect_uris']
        c.request_url = challenge['request_url']
        c.username = ''
        c.user_id = challenge['subject']
        c.skip = challenge['skip']
        c.data = json.dumps(challenge)
        return c

    def store_login_challenge(self, session, challenge):
        c = self.get_challenge(challenge)
        session.add(c)

    def get_login_challenge(self, session, challenge) -> LoginChallenge:
        q = session.query(LoginChallenge).filter(LoginChallenge.challenge == challenge).one_or_none()
        return q


    def store_consent_challenge(self, session, challenge):
        c = ConsentChallenge()
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

    def get_consent_challenge(self, session, challenge):
        q = session.query(ConsentChallenge).filter(ConsentChallenge.challenge == challenge).one_or_none()
        return q

