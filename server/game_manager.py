# server/game_manager.py
import threading
from .player import Player
try:
    from common.utils import save_match_history
except ImportError:
    def save_match_history(p1, p2, w): print(f"Fallback Save: {p1} vs {p2}, Winner: {w}")

class GameManager:
    def __init__(self):
        self.clients = {}
        self.matches = {}
        self.player_roles = {}
        self.lock = threading.Lock()
        self.waiting_player = None
        print("--- [LOG] GameManager initialized. ---")

    def register_player(self, conn, addr, username):
        print(f"--- [GM-LOG] Attempting to register '{username}' ---")
        with self.lock:
            print(f"--- [GM-LOG] Lock acquired. Checking duplicate username. ---")
            if username in self.clients:
                print(f"--- [GM-LOG] '{username}' is already in self.clients. Registration failed. ---")
                return None, None
            
            new_player = Player(conn, addr, username)
            self.clients[username] = new_player
            print(f"--- [GM-LOG] '{username}' added to clients. ---")
            
            if self.waiting_player:
                print(f"--- [GM-LOG] Found waiting player: {self.waiting_player.username} ---")
                opponent = self.waiting_player
                self.waiting_player = None
                
                self.matches[new_player.username] = opponent.username
                self.matches[opponent.username] = new_player.username
                self.player_roles[new_player.username] = 1 # O
                self.player_roles[opponent.username] = 2 # X
                
                print(f"--- [GM-LOG] Match created: {new_player.username} (1) vs {opponent.username} (2). Releasing lock. ---")
                return new_player, opponent
            else:
                self.waiting_player = new_player
                print(f"--- [GM-LOG] No waiting player. Set '{username}' as waiting. Releasing lock. ---")
                return new_player, None

    def process_message(self, player, message):
        print(f"--- [GM-LOG] Processing message from '{player.username}': {repr(message)} ---")
        opponent = self.get_opponent(player)
        if not opponent:
            print(f"--- [GM-LOG] Player '{player.username}' has no opponent. Ignoring message. ---")
            return

        if message.startswith("MOVE:"):
            print(f"--- [GM-LOG] Forwarding MOVE to '{opponent.username}' ---")
            opponent.send(f"OP_MOVE:{message.split(':', 1)[1]}")
            opponent.send("TURN")
        elif message == "WIN":
            print(f"--- [GM-LOG] '{player.username}' reported WIN. Forwarding OP_WIN to '{opponent.username}' ---")
            opponent.send("OP_WIN")
            save_match_history(player.username, opponent.username, player.username)
        elif message == "DRAW":
            print(f"--- [GM-LOG] '{player.username}' reported DRAW. Forwarding OP_DRAW to '{opponent.username}' ---")
            opponent.send("OP_DRAW")
            save_match_history(player.username, opponent.username, "DRAW")
        else:
            print(f"--- [GM-LOG] Unknown message type from '{player.username}': {repr(message)} ---")

    def get_opponent(self, player):
        print(f"--- [GM-LOG] Getting opponent for '{player.username}' ---")
        with self.lock:
            opponent_name = self.matches.get(player.username)
            if opponent_name:
                opp = self.clients.get(opponent_name)
                print(f"--- [GM-LOG] Found opponent: {opponent_name} ---")
                return opp
        print(f"--- [GM-LOG] No opponent found. ---")
        return None

    def handle_disconnect(self, player):
        print(f"--- [GM-LOG] Handling disconnect for '{player.username}' ---")
        with self.lock:
            print(f"--- [GM-LOG] Lock acquired for disconnect. ---")
            if player.username not in self.clients:
                print(f"--- [GM-LOG] '{player.username}' not in clients (already handled?). Releasing lock. ---")
                return
            
            print(f"--- [GM-LOG] Removing '{player.username}' from clients. ---")
            del self.clients[player.username]

            if self.waiting_player == player:
                print(f"--- [GM-LOG] '{player.username}' was the waiting player. Resetting waiting_player. ---")
                self.waiting_player = None
            
            opponent_name = self.matches.get(player.username)
            if opponent_name:
                print(f"--- [GM-LOG] '{player.username}' was in a match with '{opponent_name}'. ---")
                opponent = self.clients.get(opponent_name)
                
                if opponent:
                    print(f"--- [GM-LOG] Sending OP_LEFT to '{opponent.username}'. ---")
                    opponent.send("OP_LEFT")
                
                print(f"--- [GM-LOG] Cleaning up match/role entries. ---")
                del self.matches[player.username]
                if opponent_name in self.matches:
                    del self.matches[opponent_name]
                if player.username in self.player_roles:
                    del self.player_roles[player.username]
                if opponent_name in self.player_roles:
                    del self.player_roles[opponent_name]
                
                save_match_history(player.username, opponent_name, f"{opponent_name} (Disconnect)")
            print(f"--- [GM-LOG] Disconnect handling for '{player.username}' complete. Releasing lock. ---")