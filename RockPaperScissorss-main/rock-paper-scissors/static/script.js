let socket = io();
let username = '';
let room = '';
let role = '';

document.getElementById('playWithComputerBtn').addEventListener('click', () => {
    username = document.getElementById('username').value.trim();
    if (username) {
        window.location.href = `/play_computer?username=${encodeURIComponent(username)}`;
    }
});

document.getElementById('playWithFriendBtn').addEventListener('click', () => {
    document.getElementById('friend-options').style.display = 'block';
});

document.getElementById('joinFriendBtn').addEventListener('click', () => {
    username = document.getElementById('username').value.trim();
    room = document.getElementById('room').value.trim();
    if (username && room) {
        socket.emit('join', { username, room });
    }
});

document.getElementById('rockBtn').addEventListener('click', () => makeChoice('rock'));
document.getElementById('paperBtn').addEventListener('click', () => makeChoice('paper'));
document.getElementById('scissorsBtn').addEventListener('click', () => makeChoice('scissors'));
document.getElementById('sendBtn').addEventListener('click', sendMessage);

socket.on('joined', (data) => {
    document.querySelector('.mode-selection').style.display = 'none';
    document.querySelector('.game').style.display = 'block';
    role = data.role;
    document.getElementById('roleInfo').textContent = `You are ${role}`;
    document.getElementById('info').textContent = data.message;
});

socket.on('room_full', (data) => {
    alert(data.message);
});

socket.on('result', (data) => {
    let choices = data.choices;
    let scores = data.scores;
    let round = data.round;

    document.getElementById('info').textContent = `Round ${round}: ${Object.keys(choices)[0]} chose ${choices[Object.keys(choices)[0]]} | ${Object.keys(choices)[1]} chose ${choices[Object.keys(choices)[1]]}`;
    document.getElementById('result').textContent = data.result;

    let scoreboard = '';
    for (let player in scores) {
        scoreboard += `${player}: ${scores[player]} wins<br>`;
    }
    document.getElementById('scoreboard').innerHTML = scoreboard;

    if (data.final_winner) {
        document.getElementById('result').textContent = `${data.final_winner} wins the match! 🎉`;
    }
});

socket.on('chat', (data) => {
    let msg = document.createElement('div');
    msg.textContent = `${data.username}: ${data.message}`;
    document.getElementById('messages').appendChild(msg);
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
});

function makeChoice(choice) {
    socket.emit('choice', { username, choice });
    document.getElementById('info').textContent = `You chose ${choice}. Waiting for opponent...`;
}

function sendMessage() {
    let msg = document.getElementById('chatInput').value;
    if (msg.trim() !== '') {
        socket.emit('chat', { username, message: msg });
        document.getElementById('chatInput').value = '';
    }
}
