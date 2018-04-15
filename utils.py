import json
from typing import Type

import tornado.web
from marshmallow import Schema


class Routers(object):
    _routers = []

    def __init__(self, url, name=None):
        self.url = url
        self.name = name

    def __call__(self, handler):
        name = self.name or handler.__class__
        self._routers.append(
            tornado.web.url(self.url, handler, name=name)
        )

    @classmethod
    def get_routers(cls):
        return cls._routers


def validate_payload(schema: Type[Schema]):
    def decor(func):
        async def wrap(self: tornado.web.RequestHandler, *args, **kwargs):
            row_data = self.request.arguments
            json_data = \
                {k: v[0] if len(v) <= 1 else v for k, v in row_data.items()}
            errors = schema(json_data).validate(json_data)
            if errors:
                return self.send_error(400, reason=json.dumps(errors))
            res = func(self, *args, **kwargs)
            return await res

        return wrap

    return decor
