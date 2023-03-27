from random import choice, sample
from User import User
from data import pages, emojis
from pymongo import MongoClient

ROOM_LIMIT = 8

uri = "mongodb+srv://devwikiracing.lifgoh4.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='X509-cert-7030048765736591719.pem')

db = client['WikiRacing']
rooms = db['Rooms']

class Room:
    def __init__(self, room_code):
        self.room_code = room_code
        room = rooms.find_one({'_id': room_code})

        if room is None:
            start_page, target_page = choice(pages)
            room = {'_id': room_code, 
                    'users': {}, 
                    'start_page': start_page,
                    'target_page': target_page,
                    'round': 1,
                    'emojis': sample(emojis, ROOM_LIMIT)}

            rooms.insert_one(room)

    @staticmethod
    def get_all_rooms():
        room_list = list(rooms.find({}))
        return {room['_id']: room for room in room_list}

    @staticmethod
    def room_from_user(user_id):
        room_code = rooms.find_one({f'users.{user_id}.user_id': user_id})['_id']
        return Room(room_code)
    
    @staticmethod
    def exists(room_code):
        return rooms.count_documents({'_id': room_code}) > 0

    @property
    def room(self):
        return rooms.find_one({'_id': self.room_code})

    @property
    def start_page(self):
        return self.room['start_page']

    @property
    def target_page(self):
        return self.room['target_page']

    def set_time(self, user_id, time):
        rooms.update_one({'_id': self.room_code}, {'$set': {f'users.{user_id}.time': time}})
    
    def get_emoji(self, user_id):
        return self.room['users'][user_id]['emoji']

    def get_user(self, user_id):
        return self.room['users'].get(user_id, None)
    
    def add_user(self, username, user_id):
        if self.get_user(user_id) is not None:
            return # raise error here?
        
        admin_status = len(self.room['users']) == 0

        user = {'user_id': user_id,
                'username': username,
                'admin': admin_status,
                'current_page': None,
                'clicks': 0,
                'wins': 0,
                'time': 0,
                'emoji': self.room['emojis'].pop()}
        
        rooms.update_one({'_id': self.room_code}, {'$set': {f'users.{user_id}': user},
                                                   '$pop': {'emojis': 1}})

    def delete_user(self, user_id):
        deleted_user = self.get_user(user_id)

        if deleted_user is None:
            return # raise error here?

        rooms.update_one({'_id': self.room_code}, {'$unset': {f'users.{user_id}': {'user_id': user_id}}})

        if self.empty:
            rooms.delete_one({'_id': self.room_code})

        elif deleted_user['admin']:
            new_admin = next(iter(self.room['users']))
            rooms.update_one({'_id': self.room_code}, {'$set': {f'users.{new_admin}.admin': True}})

        return deleted_user

    #ROOM METHODS
    def _randomize_pages(self):
        start_page, target_page = choice(pages)
        rooms.update_one({'_id': self.room_code}, {'$set': {'start_page': start_page,
                                                            'target_page': target_page}})

    @property
    def empty(self):
        return len(self.room['users']) == 0

    @property
    def full(self):
        return len(self.room['users']) >= ROOM_LIMIT

    def start_game(self):
        #Resets relevant user statistics for next round
        start_page = self.room['start_page']
        for user_id in self.room['users']:
            rooms.update_one({'_id': self.room_code}, {'$set': {f'users.{user_id}.clicks': 0,
                                                                f'users.{user_id}.current_page': start_page}})

    def update_game(self, user_id, page):
        #user = self.get_user(user_id)
        rooms.update_one({'_id': self.room_code}, {'$inc': {f'users.{user_id}.clicks': 1}, 
                                                   '$set': {f'users.{user_id}.current_page': page}})

        user_page = page.lower()
        target_page = self.room['target_page'].lower()

        # Return winner data using end_game method
        if user_page == target_page:
            return self.end_game(user_id)
        
        return None

    def end_game(self, winner_id):
        winner = self.get_user(winner_id)

        rooms.update_one({'_id': self.room_code}, {'$inc': {f'round': 1, 
                                                            f'users.{winner_id}.wins': 1}})        

        self._randomize_pages()

        return winner

    def export(self):
        return self.room
    

if __name__ == '__main__':
    #room = Room(3456)
    #room.add_user('sameer', '123456789')
    #room.add_user('vimal', '345345345')
    #room.delete_user('123456789')
    #room.start_game()
    #room.update_game('345345345', 'Durham,_England')
    #room.update_game('123456789', 'Thermonuclear_weapon')
    #room.update_game('345345345', 'American_Museum_of_Natural_History')
