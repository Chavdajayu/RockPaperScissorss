from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

players = {}  # {username: {room, choice, wins, role}}
rooms = {}    # {room: {round, players}}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play_computer')
def play_computer():
    username = request.args.get('username', 'Player')
    return render_template('play_computer.html', username=username)

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']

    if room not in rooms:
        rooms[room] = {'round': 1, 'players': []}

    if len(rooms[room]['players']) >= 2:
        emit('room_full', {'message': 'Room is full!'}, to=request.sid)
        return

    role = 'Player 1' if len(rooms[room]['players']) == 0 else 'Player 2'
    rooms[room]['players'].append(username)

    join_room(room)
    players[username] = {'room': room, 'choice': None, 'wins': 0, 'role': role}

    emit('joined', {'role': role, 'message': f'You joined as {role}.'}, to=request.sid)

@socketio.on('choice')
def handle_choice(data):
    username = data['username']
    choice = data['choice']
    room = players[username]['room']

    players[username]['choice'] = choice

    room_players = rooms[room]['players']
    if len(room_players) == 2 and all(players[p]['choice'] for p in room_players):
        p1, p2 = room_players
        c1, c2 = players[p1]['choice'], players[p2]['choice']
        result = determine_winner(p1, c1, p2, c2)

        # Update wins
        if result['winner']:
            players[result['winner']]['wins'] += 1

        response = {
            'round': rooms[room]['round'],
            'choices': {p1: c1, p2: c2},
            'result': result['message'],
            'scores': {p1: players[p1]['wins'], p2: players[p2]['wins']}
        }

        if players[p1]['wins'] >= 3 or players[p2]['wins'] >= 3:
            response['final_winner'] = p1 if players[p1]['wins'] >= 3 else p2
            players[p1]['wins'] = 0
            players[p2]['wins'] = 0
            rooms[room]['round'] = 1
        else:
            rooms[room]['round'] += 1

        players[p1]['choice'] = None
        players[p2]['choice'] = None

        socketio.emit('result', response, room=room)

@socketio.on('chat')
def handle_chat(data):
    room = players[data['username']]['room']
    emit('chat', {'username': data['username'], 'message': data['message']}, room=room)

def determine_winner(p1, c1, p2, c2):
    if c1 == c2:
        return {'winner': None, 'message': "It's a Draw!"}
    elif (c1 == 'rock' and c2 == 'scissors') or (c1 == 'scissors' and c2 == 'paper') or (c1 == 'paper' and c2 == 'rock'):
        return {'winner': p1, 'message': f'{p1} wins the round!'}
    else:
        return {'winner': p2, 'message': f'{p2} wins the round!'}

if __name__ == "__main__":
    app.run(debug=True)
