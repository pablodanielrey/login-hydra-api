import os

HYDRA_ADMIN_URL = os.environ.get('HYDRA_ADMIN_URL')
VERIFY_HTTPS = bool(int(os.environ.get('VERIFY_HTTPS',0)))

from hydra.model.HydraModel import HydraModel
from hydra.model.HydraLocalModel import HydraLocalModel
from hydra.model.QRModel import QRModel
from login.model.LoginModel import LoginModel
from users.model.UsersModel import UsersModel

hydraModel = HydraModel(HYDRA_ADMIN_URL, VERIFY_HTTPS)
hydraLocalModel = HydraLocalModel()
loginModel = LoginModel()
usersModel = UsersModel()
qrModel = QRModel()