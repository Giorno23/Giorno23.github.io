from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

# Создание базы данных
def create_db():
    conn = sqlite3.connect('messenger.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, receiver TEXT NOT NULL, message TEXT NOT NULL)''')
    conn.commit()
    conn.close()

create_db()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница чата
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        sender = request.form['sender']
        receiver = request.form['receiver']
        message = request.form['message']
        conn = sqlite3.connect('messenger.db')
        c = conn.cursor()
        c.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (sender, receiver, message))
        conn.commit()
        conn.close()
        return redirect(url_for('chat'))
    return render_template('chat.html')

# WebSocket-обработчики для обмена сообщениями
@socketio.on('send_message')
def handle_send_message(data):
    sender = data['sender']
    receiver = data['receiver']
    message = data['message']
    conn = sqlite3.connect('messenger.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (sender, receiver, message))
    conn.commit()
    conn.close()
    emit('receive_message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
