from random import choice, sample
from data import pages, emojis
from pymongo import MongoClient

ROOM_LIMIT = 8

uri = "mongodb+srv://devwikiracing.lifgoh4.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='X509-cert.pem')

db = client['WikiRacing']
rooms = db['Rooms']

class Room:
    def __init__(self, room_code):
        self.room_code = room_code
        room = rooms.find_one({'_id': room_code})

        # Only add room to collection if it doesn't already exist
        if room is None:
            start_page, target_page = choice(pages)
            room = {'_id': room_code,
                    'users': {},
                    'start_page': start_page,
                    'target_page': target_page,
                    'round': 1,
                    'emojis': sample(sorted(emojis), ROOM_LIMIT)}

            rooms.insert_one(room)

    #ROOM PROPERTIES
    @property
    def room(self):
        return rooms.find_one({'_id': self.room_code})

    @property
    def users(self):
        return self.room['users']

    @property
    def start_page(self):
        return self.room['start_page']

    @property
    def target_page(self):
        return self.room['target_page']

    @property
    def round(self):
        return self.room['round']

    @property
    def emojis(self):
        return self.room['emojis']

    @property
    def empty(self):
        return len(self.room['users']) == 0

    @property
    def full(self):
        return len(self.room['users']) >= ROOM_LIMIT

    #STATIC METHODS (not specific to any room)
    @staticmethod
    def get_all_rooms():
        # Hopefully this function can be deleted soon because it is not good practice
        room_list = list(rooms.find({}))
        return {room['_id']: room for room in room_list}

    @staticmethod
    def room_from_user(user_id):
        room = rooms.find_one({f'users.{user_id}.user_id': user_id})
        if room:
            return Room(room['_id'])

        #room_code = rooms.find_one({f'users.{user_id}.user_id': user_id})['_id']
        return None

    @staticmethod
    def exists(room_code):
        return rooms.count_documents({'_id': room_code}) > 0

    #USER METHODS
    def set_user_field(self, user_id, field, data):
        rooms.update_one({'_id': self.room_code}, {'$set': {f'users.{user_id}.{field}': data}})

    def get_user_field(self, user_id, field):
        return self.get_user(user_id).get(field, None)

    def get_user(self, user_id):
        return self.users.get(user_id, None)

    def add_user(self, username, user_id):
        if self.get_user(user_id) is not None:
            return # raise error here?

        admin_status = self.empty

        user = {'user_id': user_id,
                'username': username,
                'admin': admin_status,
                'current_page': None,
                'clicks': 0,
                'wins': 0,
                'time': 0,
                'emoji': self.emojis.pop()}

        rooms.update_one({'_id': self.room_code}, {'$set': {f'users.{user_id}': user},
                                                   '$pop': {'emojis': 1}})

    def delete_user(self, user_id):
        deleted_user = self.get_user(user_id)

        if deleted_user is None:
            return # raise error here?

        rooms.update_one({'_id': self.room_code}, {'$unset': {f'users.{user_id}': {'user_id': user_id}}})

        # if last user left, delete the room from database
        if self.empty:
            rooms.delete_one({'_id': self.room_code})

        # if the user to leave is admin and other users are left, choose a new admin
        elif deleted_user['admin']:
            new_admin = next(iter(self.users))
            rooms.update_one({'_id': self.room_code}, {'$set': {f'users.{new_admin}.admin': True}})

        return deleted_user

    #ROOM METHODS
    def _randomize_pages(self):
        start_page, target_page = choice(pages)
        rooms.update_one({'_id': self.room_code}, {'$set': {'start_page': start_page,
                                                            'target_page': target_page}})

    def start_game(self):
        #Resets relevant user statistics for next round
        start_page = self.start_page
        for user_id in self.users:
            rooms.update_one({'_id': self.room_code}, {'$set': {f'users.{user_id}.clicks': 0,
                                                                f'users.{user_id}.current_page': start_page}})

    def update_game(self, user_id, page):
        rooms.update_one({'_id': self.room_code}, {'$inc': {f'users.{user_id}.clicks': 1},
                                                   '$set': {f'users.{user_id}.current_page': page}})

        user_page = page.lower()
        target_page = self.target_page.lower()

        # Return winner data using end_game method
        if user_page == target_page:
            return self.end_game(user_id)

        return None

    def end_game(self, winner_id):
        winner = self.get_user(winner_id)

        if winner is None:
            return

        rooms.update_one({'_id': self.room_code}, {'$inc': {f'round': 1,
                                                            f'users.{winner_id}.wins': 1}})

        self._randomize_pages()

        return winner

    def export(self):
        to_export = self.room

        # switch from MongoDB use to internal use
        to_export['room_code'] = to_export.pop('_id')

        return to_export

