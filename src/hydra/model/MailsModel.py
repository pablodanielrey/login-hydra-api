
import os
import base64
import requests
from jinja2 import Environment, PackageLoader, FileSystemLoader

class MailsModel:

    #EMAILS_API_URL = os.environ['EMAILS_API_URL']

    def __init__(self, emails_api):
        self.emails_api = emails_api
        self.env = Environment(loader=PackageLoader('hydra.model.templates','.'))

    def get_template(self, template):
        templ = self.env.get_template(template)
        return templ

    def send_email(self, from_, to, subject, body):
        ''' https://developers.google.com/gmail/api/guides/sending '''
        bbody = base64.urlsafe_b64encode(body.encode('utf-8')).decode()
        r = requests.post(f'{self.emails_api}/correos/', json={'sistema':'login', 'de':from_, 'para':to, 'asunto':subject, 'cuerpo':bbody})
        return r
