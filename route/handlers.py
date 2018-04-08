import asyncio
import operator
from itertools import zip_longest

import aiohttp
import pymongo

from handlers import BaseHandler
from route.models import Route, RoutePoint
from route.serializers import UserTopSchema
from settings import USER_SERVICE
from utils import Routers


@Routers("/route")
class RouterPath(BaseHandler):
    model = Route

    async def post(self, *args, **kwargs):
        payload = self.fill_payload(author=self.get_current_user)
        insert = (await Route(**payload).commit()).inserted_id
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
        chuncks = zip_longest(*[iter(top_users)] * 5)

        users = {}
        async with self.get_session() as session:
            for ch in chuncks:
                users_chunck = await asyncio.gather(*[self.get_body(session, user["_id"]) for user in ch if user])
                [users.update(
                    {u['guid']: u}) for u in users_chunck]

        [operator.setitem(u, "user", users.get(str(u['_id']), None)) for u in top_users]
        data = self.dumps(top_users, many=True)
        self.write(data)

    def get_session(self):
        session = aiohttp.ClientSession()
        return session

    async def get_body(self, session, guid):
        url = USER_SERVICE + "/" + str(guid)
        response = await session.get(url)
        data = await response.json()
        return data

@Routers("/last")
class Last5Route(BaseHandler):
    schema = Route.Schema

    async def get(self):
        cursor = Route.find({}).sort([("created", pymongo.ASCENDING)]).limit(5)
        last_routers = await cursor.to_list(None)
        data = self.dumps(last_routers, True)
        self.write(data)
