from tinydb import TinyDB, Query

db = TinyDB('device_management_db.json')
users_table = db.table('users')

class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def store_data(self):
        users_table.insert(self.__dict__)

    @classmethod
    def find_all(cls):
        return [cls(**user) for user in users_table.all()]

    @classmethod
    def delete(cls, user_id):
        UserQuery = Query()
        users_table.remove(UserQuery.id == user_id)
