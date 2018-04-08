from abc import abstractmethod

import tornado.escape
import tornado.web
from umongo import Document


class BaseHandler(tornado.web.RequestHandler):
    @property
    @abstractmethod
    def model(self) -> Document:
        pass

    @property
    def payload(self) -> dict:
        return tornado.escape.json_decode(self.request.body)

    def fill_payload(self, **extra):
        payload = dict((k, self.payload.get(k)) for k in self.model.DataProxy._fields if k in self.payload)
        for k, v in extra.items():
            payload[k] = v() if callable(v) else v
        return payload

    def get_current_user(self):
        # return self.get_cookie("username")
        return self.payload['user']

    def dumps(self, obj, many=False):
        sh = self.schema(many=many, strict=True)
        res = sh.dumps(obj, True)
        return res.data
