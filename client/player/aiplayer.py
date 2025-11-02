# client/player/aiplayer.py
# Class này để định nghĩa một Người chơi (AI)
from client.logic import ai

class AIPlayer:
    def __init__(self, piece_id, difficulty="hard"):
        self.username = "Máy"
        self.piece_id = piece_id
        self.difficulty = difficulty

    def get_move(self, board_state):
        """
        Tính toán và trả về nước đi (y, x) của AI.
        """
        # (SỬA) Gọi hàm AI từ module logic.ai
        if self.difficulty == "hard":
            y, x = ai.best_move(board_state, self.piece_id)
            return y, x
        else:
            # TODO: Thêm logic cho AI 'dễ' (ví dụ: nước đi ngẫu nhiên)
            y, x = ai.best_move(board_state, self.piece_id) # Tạm dùng 'hard'
            return y, x