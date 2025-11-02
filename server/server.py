# server/server.py
import socket
import threading
from .game_manager import GameManager
from .player import Player
from common.constants import HOST, PORT
import traceback 

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.game_manager = GameManager()
        self.running = True
        self.client_threads = []

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.settimeout(1.0)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"--- [LOG] Server is listening on {self.host}:{self.port} ---")

        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
                self.client_threads.append(thread)
            except socket.timeout:
                pass
            except OSError:
                if self.running:
                    print("--- [WARN] Error accepting connection. ---")
                break 

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("--- [LOG] Server stopped. ---")

    def handle_client(self, conn, addr):
        print(f"--- [LOG] New connection from {addr} ---")
        player = None
        buffer = ""
        try:
            # 1. Login
            print(f"[{addr}] Waiting for LOGIN message...")
            # Nhận data (có thể là 1 hoặc nhiều tin nhắn)
            login_data = conn.recv(1024).decode('utf-8')
            if not login_data:
                raise ConnectionAbortedError("Client disconnected before login")
            
            print(f"[{addr}] Received data: {repr(login_data)}")
            buffer += login_data
            
            if '\n' not in buffer:
                raise ConnectionAbortedError(f"Invalid login (no newline): {repr(buffer)}")
                
            # Tách tin nhắn login (message ĐẦU TIÊN)
            message, buffer = buffer.split('\n', 1) 
            print(f"[{addr}] Processing login message: {repr(message)}")
            
            if not message.startswith("LOGIN:"):
                raise ConnectionAbortedError("Invalid login request")

            username = message.split(":", 1)[1].strip()
            if not username:
                raise ConnectionAbortedError("Empty username")
            
            print(f"[{addr}] Username stripped: {repr(username)}")

            # 2. Register
            print(f"[{addr}] Registering player {username}...")
            player, opponent = self.game_manager.register_player(conn, addr, username)
            
            if player is None: # Tên đã tồn tại
                print(f"[{addr}] Username {username} taken. Sending FAIL.")
                conn.sendall("LOGIN_FAIL:Username taken\n".encode('utf-8'))
                raise ConnectionAbortedError("Username taken")
            
            print(f"[{addr}] Login OK. Sending LOGIN_OK.")
            conn.sendall("LOGIN_OK\n".encode('utf-8'))

            # 3. Matchmaking
            if opponent:
                print(f"[{addr}] Match found for {username} vs {opponent.username}!")
                player.send(f"MATCH:{opponent.username},1")
                opponent.send(f"MATCH:{player.username},2")
                player.send("START")
                opponent.send("START")
                player.send("TURN")
                print(f"[{addr}] Sent MATCH/START/TURN to both players.")
            else:
                print(f"[{addr}] {username} is waiting. Sending WAITING.")
                player.send("WAITING")

            # 4. Game Loop
            print(f"[{addr}] Entering game loop, remaining buffer: {repr(buffer)}")
            while self.running:
                # Xử lý TẤT CẢ message còn lại trong buffer TRƯỚC KHI đợi
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message:
                        print(f"[{addr}] Processing buffered message: {repr(message)}")
                        self.game_manager.process_message(player, message)
                
                # Hết message trong buffer, đợi tin nhắn mới
                print(f"[{addr}] Waiting for new data...")
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    raise ConnectionResetError("Client disconnected")
                
                print(f"[{addr}] Received new data: {repr(data)}")
                buffer += data
                # Vòng lặp while self.running sẽ quay lại,
                # và vòng lặp while '\n' in buffer sẽ xử lý data mới này.

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            print(f"--- [WARN] Client {addr} (User: {player.username if player else 'Unknown'}) disconnected: {e} ---")
        except Exception as e:
            # IN RA LỖI CHI TIẾT
            print(f"--- [ERROR] CRASH in handle_client for {addr} (User: {player.username if player else 'Unknown'}) ---")
            print(traceback.format_exc())
        finally:
            print(f"--- [LOG] Cleaning up connection for {addr} (User: {player.username if player else 'Unknown'}) ---")
            if player:
                self.game_manager.handle_disconnect(player)
            conn.close()