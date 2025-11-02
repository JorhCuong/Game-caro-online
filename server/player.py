# server/player.py
import socket

class Player:
    def __init__(self, connection, addr, username):
        self.conn = connection
        self.addr = addr
        self.username = username
        self.opponent_name = None # Sẽ được set bởi GameManager

    def send(self, message):
        try:
            if not message.endswith('\n'):
                message += '\n' 
            self.conn.sendall(message.encode('utf-8'))
        except (BrokenPipeError, OSError) as e:
            print(f"Failed to send to {self.username}: {e}")

    def __str__(self):
        return f"Player(username='{self.username}', addr={self.addr})"