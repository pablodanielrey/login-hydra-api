import os

HYDRA_ADMIN_URL = os.environ.get('HYDRA_ADMIN_URL')
VERIFY_HTTPS = bool(int(os.environ.get('VERIFY_HTTPS',0)))

from login.hydra.model.HydraModel import HydraModel
from login.hydra.model.LogModel import LogModel
from login.model.LoginModel import LoginModel

hydraModel = HydraModel(HYDRA_ADMIN_URL, VERIFY_HTTPS)
logModel = LogModel()
loginModel = LoginModel()