import asyncio
import re

import cloudinary.uploader
import tornado
from motor.motor_asyncio import AsyncIOMotorClient
from tornado.web import Application
from umongo import MotorAsyncIOInstance
from umongo.document import MetaDocumentImplementation
from umongo.template import MetaTemplate

import settings
from utils import Routers


class WliImagesApplication(Application):
    db = AsyncIOMotorClient(settings.MONGO_HOST).wli
    db_instance = MotorAsyncIOInstance()
    db_instance.init(db)

    def __init__(self):
        cloudinary.config(
            **settings.CLOUDINARY
        )
        self.register_models()
        hadlers = self.register_handlers()
        super(WliImagesApplication, self).__init__(hadlers)

    def register_models(self):
        for app_path in settings.APPS:
            __import__(app_path, globals(), locals(), ['models'])

    def register_handlers(self):
        for app_path in settings.APPS:
            __import__(app_path, globals(), locals(), ['handlers'])
        return Routers.get_routers()


class MetaBaseModel(type):
    def __new__(cls, name, bases, attrs: dict, **kwargs):
        klass = super().__new__(cls, name, bases, attrs, **kwargs)
        db_instance = cls.db_instance()
        klass = db_instance.register(klass)
        return klass

    @staticmethod
    def db():
        return WliImagesApplication.db

    @staticmethod
    def db_instance():
        return WliImagesApplication.db_instance

    @property
    def uploader(cls):
        return WliImagesApplication.uploader


class MetaBaseTemplate(MetaBaseModel, MetaTemplate):
    class Meta:
        pass


def main():
    return WliImagesApplication()


async def create_index():
    for app_path in settings.APPS:
        models = __import__(app_path, globals(), locals(), ['models']).models

        for name in (m for m in dir(models) if re.match(r'[A-Z]', m)):
            model = getattr(models, name)

            if isinstance(model, MetaDocumentImplementation):
                await model.ensure_indexes()


if __name__ == '__main__':
    app = main()
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    app.listen(3004)
    asyncio.get_event_loop().run_until_complete(create_index())
    asyncio.get_event_loop().run_forever()
