# client/logic/game.py

# File này có thể dùng để quản lý trạng thái game (Game State)
# ví dụ: ai đang chơi, game đã bắt đầu chưa,
# và điều phối giữa Board, Player, và AIPlayer.

class GameLogic:
    def __init__(self, board, player1, player2):
        self.board = board
        self.player1 = player1
        self.player2 = player2
        self.current_turn = player1
        self.game_started = False

    def start_game(self):
        self.game_started = True
        self.board.reset_board()

    def switch_turn(self):
        if self.current_turn == self.player1:
            self.current_turn = self.player2
        else:
            self.current_turn = self.player1