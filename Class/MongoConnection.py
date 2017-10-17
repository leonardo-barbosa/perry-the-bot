from pymongo import MongoClient
import os

class MongoConnection:
    def __init__(self):
        self._db_url = "mongodb://{0}:{1}@ds149124.mlab.com:49124/perry-bot"\
            .format(os.environ.get('MONGO_USER', None), os.environ.get('MONGO_PASS', None))
        self._client = MongoClient(self._db_url, connectTimeoutMS=30000)
        self._db = self._client.get_database("perry-bot")

    def get_active_supporters(self):
        sups = []
        try:
            collection = self._db.users_records
            supporters = collection.find()

            for sup in supporters:
                if sup['status'] == "active":
                    sups.append(sup)
        except Exception as e:
            print(e.args)

        return sups

    def get_suporters_by_zendesk_id(self, id):
        try:
            collection = self._db.users_records
            supporters = collection.find()
            for sup in supporters:
                if str(sup['zendesk_id']) == str(id):
                    return sup
        except Exception as e:
            print(e.args)
