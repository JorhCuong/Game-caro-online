# client/logic/board.py
import random

class CaroGame:
    def __init__(self):
        """
        Khởi tạo logic game, bao gồm bàn cờ.
        - 0: Ô trống
        - 1: Quân O (người chơi 1)
        - 2: Quân X (người chơi 2)
        """
        self.board = [[0 for _ in range(25)] for _ in range(25)]

    def make_move(self, y, x, player_id):
        """Thực hiện một nước đi trên bàn cờ."""
        if self.is_in(y, x) and self.board[y][x] == 0:
            self.board[y][x] = player_id
            return True
        return False

    def reset_board(self):
        """Làm mới lại bàn cờ, tất cả các ô về 0."""
        for row in self.board:
            for i in range(len(row)):
                row[i] = 0
    
    def check_win_and_get_line(self, last_y, last_x):
        """
        Kiểm tra xem nước đi cuối cùng tại (last_y, last_x) có tạo ra một dãy 5 quân không.
        Nếu có, trả về (tên người thắng, (tọa độ bắt đầu, tọa độ kết thúc)).
        Nếu không, trả về (None, None).
        """
        player_id = self.board[last_y][last_x]
        if player_id == 0:
            return None, None

        # Các hướng để kiểm tra: ngang, dọc, chéo chính, chéo phụ
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dy, dx in directions:
            line = [(last_y, last_x)]
            
            # Đếm về một phía
            for i in range(1, 5):
                y, x = last_y + i * dy, last_x + i * dx
                if self.is_in(y, x) and self.board[y][x] == player_id:
                    line.append((y, x))
                else:
                    break
            
            # Đếm về phía ngược lại
            for i in range(1, 5):
                y, x = last_y - i * dy, last_x - i * dx
                if self.is_in(y, x) and self.board[y][x] == player_id:
                    line.append((y, x))
                else:
                    break
            
            # Kiểm tra đủ 5
            if len(line) >= 5:
                # Sắp xếp lại line để lấy điểm đầu và cuối
                line.sort()
                start_point = line[0]
                end_point = line[-1]
                winner_name = "O won" if player_id == 1 else "X won"
                return winner_name, (start_point, end_point)

        return None, None

    def is_in(self, y, x):
        """Kiểm tra (y, x) có nằm trong bàn cờ không."""
        return 0 <= y < 25 and 0 <= x < 25