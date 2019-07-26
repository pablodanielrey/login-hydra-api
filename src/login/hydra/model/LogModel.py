
import json

from .entities.Hydra import ChallengeLog

class LogModel:

    def log_challenge(self, session, challenge):
        c = ChallengeLog()
        c.created = datetime.datetime.utcnow()
        c.client_id = challenge['client']['client_id']
        c.client_name = challenge['client']['client_name']
        c.client_url = challenge['client']['client_uri']
        c.username = ''
        c.user_id = challenge['subject']
        c.skip = challenge['skip']
        c.data = json.dumps(challenge)
        session.add(c)

    def get_log_challenges(self, session):
        q = session.query(ChallengeLog).order_by(ChallengeLog.created.desc()).all()
        return q