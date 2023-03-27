from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask_cors import CORS, cross_origin
from Room import Room
from Page import Page
from better_profanity import profanity
import requests
import requests_cache

app = Flask(__name__)
cors = CORS(app)

app.config.from_object('config.ProdConfig')

socketio = SocketIO(app, cors_allowed_origins="*")

requests_cache.install_cache()

@app.route('/')
def hello():
    return 'This is the backend server for wikiracing.io.'

@app.route('/validation_data')
@cross_origin()
def validation():
    #TODO: FIX THIS, THIS SUCKS
    return Room.get_all_rooms()

@socketio.on('join')
def on_join(data):
    username = data['userName']
    room_code = data['roomCode']
    
    #ensure that redirects dont add empty users
    if username:

        room = Room(room_code)
        
        room.add_user(username, request.sid)
        join_room(room_code)

        room_data = room.export()

        emit('updateRoom', room_data, broadcast=True, room=room_code)

        # Join message
        msg_item = {'username': 'Bot', 'emoji': '&#129302;', 'message': f'{username} joined the room.'}
        emit('chatMSG', msg_item, broadcast=True, room=room_code)

@socketio.on('disconnect')
def on_leave():

    room = Room.room_from_user(request.sid)
    deleted_user = room.delete_user(request.sid)
    room_code = room.room_code
    leave_room(room_code)
    
    # only update room if any users are left
    if Room.exists(room_code):
        room_data = room.export()
        emit('updateRoom', room_data, broadcast = True, room = room_code)

        # Leave message
        msg_item = {'username': 'Bot', 'emoji': '&#129302;', 'message': f'{deleted_user["username"]} left the room.'}
        emit('chatMSG', msg_item, broadcast=True, room=room_code)

@socketio.on('startRound')
def start_game(data):
    room_code = data['roomCode']
    room = Room(room_code)

    room.start_game()

    emit('startRound', {'startPage': room.start_page}, broadcast=True, room=room_code)

@socketio.on('updateRoom')
def update_room(data):
    room_code = data['roomCode']
    
    room = Room(room_code)

    room_data = room.export()

    emit('updateRoom', room_data, broadcast=True, room=room_code)


@socketio.on('randomizePages')
def randomize(data):
    room_code = data['roomCode']
    
    room = Room(room_code)

    room.randomize_pages()

    room_data = room.export()

    emit('updateRoom', room_data, broadcast=True, room=room_code)

@socketio.on('updatePage')
def get_wikipage(data):
    room_code = data['roomCode']
    page_name = data['wikiPage']
    
    room = Room(room_code)

    page = Page(page_name, room.target_page).export()
    emit('updatePage', page)
    
    winner = room.update_game(request.sid, page_name)

    if winner is not None:
        emit('endRound', winner, broadcast=True, room=room_code)

@socketio.on('updateTime')
def update_time(data):
    time = data['time']
    room_code = data['roomCode']

    room = Room(room_code)

    room.set_user_field(request.sid, 'time', time)

@socketio.on('chatMSG')
def message(data):
    message = profanity.censor(data['message'], '&#129324')
    user_name = data['userName']
    room_code = data['roomCode']

    room = Room(room_code)

    emoji = room.get_user_field(request.sid, 'emoji')

    msg_item = {'username': user_name, 'emoji': emoji, 'message': message}

    emit('chatMSG', msg_item, broadcast=True, room=room_code)

if __name__ == '__main__':
    app.run()


