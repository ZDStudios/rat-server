from flask import Flask, render_template, request, jsonify, send_file, Response
import threading
import socket
import os
import time
import cv2
import numpy as np
import base64

app = Flask(__name__)

clients = {}
client_lock = threading.Lock()
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# WebSocket-like streaming (simplified)
stream_data = {}

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

# Live Stream Endpoint
@app.route('/api/stream/<client_id>')
def stream(client_id):
    def generate():
        while True:
            if client_id in stream_data:
                frame = stream_data[client_id]
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Other endpoints (file upload/download, commands, etc.) remain unchanged
if __name__ == '__main__':
    threading.Thread(target=start_server_socket, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)
