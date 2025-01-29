from tinydb import TinyDB, Query

# Datenbank initialisieren
db = TinyDB('device_management_db.json')
users_table = db.table('users')

class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def store_data(self):
        """Speichert den Nutzer in der Datenbank."""
        users_table.insert(self.__dict__)

    @classmethod
    def find_all(cls):
        """Liest alle Nutzer aus der Datenbank und gibt sie als Objekte zurück."""
        return [cls(**user) for user in users_table.all()]

    @classmethod
    def find_by_id(cls, user_id):
        """Findet einen Nutzer basierend auf der ID."""
        UserQuery = Query()
        result = users_table.search(UserQuery.id == user_id)
        if result:
            return cls(**result[0])
        return None

    @classmethod
    def delete(cls, user_id):
        """Entfernt einen Nutzer aus der Datenbank."""
        UserQuery = Query()
        users_table.remove(UserQuery.id == user_id)
