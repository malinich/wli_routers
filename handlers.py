import tornado.web
import tornado.escape


class BaseHandler(tornado.web.RequestHandler):
    @property
    def payload(self) -> dict:
        return tornado.escape.json_decode(self.request.body)

    def get_current_user(self):
        return self.payload['user']

    def dumps(self, obj, many=False):
        sh = self.schema(many=many, strict=True)
        res = sh.dumps(obj, True)
        return res.data
