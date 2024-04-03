import datetime
from dateutil import parser
import json
from uuid import UUID

from fastapi import FastAPI
import orm.postgres as ORM

app = FastAPI()


class APICore:
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, UUID) or isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
                return str(obj)
            return json.JSONEncoder.default(self, obj)\

    @classmethod
    def json_reserialize(cls, obj):
        return json.loads(json.dumps(obj, cls=cls.CustomJSONEncoder))

    @staticmethod
    def validate_uuid4(uuid_string):
        try:
            uuid = UUID(uuid_string, version=4)
        except ValueError:
            raise ValueError('Invalid UUID!')
        if not str(uuid) == uuid_string:
            raise ValueError('Invalid UUID!')

    @staticmethod
    def bash_comparsion(operator, obj1, obj2):
        if operator == 'eq':
            return obj1 == obj2
        elif operator == 'ne':
            return obj1 != obj2
        elif operator == 'gt':
            return obj1 > obj2
        elif operator == 'ge':
            return obj1 >= obj2
        elif operator == 'lt':
            return obj1 < obj2
        elif operator == 'le':
            return obj1 <= obj2
        elif operator == 'contains':
            return obj1.contains(obj2)
        elif operator == 'startswith':
            return obj1.startswith(obj2)
        elif operator == 'endswith':
            return obj1.endswith(obj2)
        elif operator == 'notcontains':
            return not obj1.contains(obj2)
        else:
            raise ValueError('Invalid operator!')

    @staticmethod
    def str_to_datetime(date_string):
        try:
            return parser.parse(date_string)
        except Exception:
            return None

    @staticmethod
    def extract_page(select, page, per_page):
        if page < 1 or per_page < 1:
            return [ORM.BaseModel.extract_data_from_select_dict(el.__dict__) for el in select] # all elements

        return [ORM.BaseModel.extract_data_from_select_dict(el.__dict__)
                for el in select.paginate(page, per_page)]
