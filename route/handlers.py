import json

import pymongo
import tornado.escape
import tornado.web

from handlers import BaseHandler
from route.models import Route, RoutePoint
from route.serializers import UserTopSchema
from utils import Routers


@Routers("/route")
class RouterCreate(BaseHandler):

    async def post(self, *args, **kwargs):
        data = {
            "author": self.get_current_user(),
            "title": self.payload.get("title"),
            "vectors": self.payload.get("vectors"),
            "is_public": self.payload.get("is_public")
        }
        insert = (await Route(**data).commit()).inserted_id
        self.write(str(insert))


@Routers("/points")
class RoutePoints(BaseHandler):

    async def post(self, *args, **kwargs):
        data = {
            "route": self.payload.get("route"),
            "point": self.payload.get("point"),
            "photos": self.payload.get("photos"),
            "text": self.payload.get("text"),
            "tags": self.payload.get("tags"),
        }
        insert = (await RoutePoint(**data).commit()).inserted_id
        self.write(str(insert))


@Routers("/top")
class UsersTopRoute(BaseHandler):
    schema = UserTopSchema

    async def get(self, *args, **kwargs):
        cursor = Route.collection.aggregate([
            {"$match": {"is_public": True}},
            {"$group": {"_id": "$author",
                        "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 6}
        ])
        top_users = await cursor.to_list(None)
        data = self.dumps(top_users, many=True)
        self.write(data)


@Routers("/last")
class Last5Route(BaseHandler):
    schema = Route.Schema

    async def get(self):
        cursor = Route.find({}).sort([("created", pymongo.ASCENDING)]).limit(5)
        last_routers = await cursor.to_list(None)
        data = self.dumps(last_routers, True)
        self.write(data)
