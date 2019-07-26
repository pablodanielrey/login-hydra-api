"""
    implementa la api de hydra.
    referencia :
    https://www.ory.sh/docs/api/hydra/?version=latest
    https://www.ory.sh/docs/guides/master/hydra/3-overview/1-oauth2#implementing-a-login--consent-provider
"""
import logging
import requests

from oidc.oidc import ClientCredentialsGrant

class HydraModel:

    def __init__(self, hydra_api, verify=False):
        self.verify = verify
        self.hydra_api = hydra_api

    def get_login_challenge(self, challenge:str):
        url = f"{self.hydra_api}/oauth2/auth/requests/login"
        h = {
            'X-Forwarded-Proto':'https',
            'Accept': 'application/json'
        }
        r = requests.get(url, params={'login_challenge': challenge},headers=h, verify=self.verify)
        if r.satus_code == 200:
            return (200, r.json())
        return (r.status_code, str(r))



