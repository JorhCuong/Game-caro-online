# client/player/player.py
# Class này để định nghĩa một Người chơi (Human)

class Player:
    def __init__(self, username, piece_id):
        self.username = username
        self.piece_id = piece_id # 1 (O) or 2 (X)

    def get_move(self):
        # Người chơi (Human) không dùng hàm này
        # Nước đi được lấy từ sự kiện click chuột trên UI
        pass