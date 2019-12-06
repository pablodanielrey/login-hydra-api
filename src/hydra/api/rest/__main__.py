
import ptvsd
ptvsd.enable_attach(address = ('0.0.0.0', 10004))

from hydra.api.rest.wsgi import app
app.run(host='0.0.0.0', port=10002, debug=False)

