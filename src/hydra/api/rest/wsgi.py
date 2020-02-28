import logging
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().propagate = True


from flask import Flask
from flask_cors import CORS
#from werkzeug.contrib.fixers import ProxyFix
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.debug = False
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

"""
    registro el encoder para json
"""

from hydra.model.entities import AlchemyEncoder
app.json_encoder = AlchemyEncoder

"""
    /////////////
    registro los converters 
"""
from rest_utils.converters.ListConverter import ListConverter
app.url_map.converters['list'] = ListConverter
"""
    ////////////
"""

from . import login
#from . import qr
from . import email

app.register_blueprint(login.bp)
#app.register_blueprint(qr.bp)
app.register_blueprint(email.bp)
