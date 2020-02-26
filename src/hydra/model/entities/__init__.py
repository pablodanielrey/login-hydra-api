import os
import json
import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                if isinstance(data, (datetime.date, datetime.datetime)):
                    fields[field] = data.isoformat()
                else:
                    try:
                        ''' testeo a ver si se puede serializar '''
                        json.dumps(data)
                        fields[field] = data
                    except TypeError as e:
                        fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)

Base = declarative_base()





