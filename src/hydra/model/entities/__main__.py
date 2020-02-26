

def crear_tablas():
    import os
    from sqlalchemy import create_engine
    from .Hydra import DeviceLogins, LoginChallenge, ConsentChallenge
    from .QR import QrCode
    from . import Base

    engine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(
        os.environ['DB_USER'],
        os.environ['DB_PASSWORD'],
        os.environ['DB_HOST'],
        os.environ.get('DB_PORT',5432),
        os.environ['DB_NAME']
    ), echo=True)
    Base.metadata.create_all(engine)



crear_tablas()