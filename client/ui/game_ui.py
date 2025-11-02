# client/ui/game_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import queue
import traceback # Dùng để in lỗi (nếu có)

# (SỬA) Import theo cấu trúc package mới
from client.network.game_network import NetworkManager
from client.logic.board import CaroGame
from client.ui.board import GameBoardUI
from client.logic import ai # Import module AI

class ChessboardApp:
    def __init__(self, root, username=None, mode="offline", difficulty="hard"):
        self.root = root
        self.root.title("Five in a Row")
        self.root.configure(bg="#F0F0F0")

        style = ttk.Style()
        style.theme_use('clam')

        self.game = CaroGame()
        self.network = NetworkManager(queue.Queue())
        self.message_queue = self.network.message_queue

        self.my_turn = False
        self.my_piece_id = 0
        # (SỬA) Lấy username từ main.py
        self.username = username if username else "Player"
        self.opponent_name = ""
        self.game_started = False
        self.timer_id = None

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.difficulty = difficulty

    # ---------- (THÊM MỚI) HÀM ĐỂ VÀO GAME OFFLINE ----------
    def start_offline_game(self):
        """Hàm này được gọi bởi client/main.py khi chọn mode 'offline'"""
        self.root.title(f"Five in a Row - Offline ({self.username})")
        self.setup_game_view() # Vẽ bàn cờ
        self.status_bar.config(text="Chế độ Offline: Bạn đi trước (Quân O).")
        self.you_label.config(text=f"Bạn: {self.username} (O)")
        self.opponent_label.config(text=f"Đối thủ: Máy (X)")
        self.my_turn = True # Bạn đi trước

    # ---------- (SỬA) HÀM ĐỂ VÀO GAME ONLINE ----------
    def show_login_ui(self):
        """Hàm này được gọi bởi client/main.py khi chọn mode 'online'"""
        self.clear_main_frame()
        self.login_frame = ttk.Frame(self.main_frame)
        self.login_frame.pack(expand=True)

        ttk.Label(self.login_frame, text="KẾT NỐI SERVER", font=("Arial", 18, "bold")).pack(pady=10)
        ttk.Label(self.login_frame, text=f"Tên của bạn: {self.username}", font=("Arial", 12, "bold")).pack(pady=(10,0))
        ttk.Label(self.login_frame, text="Địa chỉ IP của Server:", font=("Arial", 12)).pack(pady=(10,0))
        
        self.ip_entry = ttk.Entry(self.login_frame, font=("Arial", 12), width=30)
        self.ip_entry.insert(0, "127.0.0.1") # Nên lấy từ common/constants
        self.ip_entry.pack(pady=5, padx=20)
        
        ttk.Button(self.login_frame, text="Tìm trận", command=self.connect_to_server).pack(pady=20, ipady=5, ipadx=10)

    def connect_to_server(self):
        ip = self.ip_entry.get().strip()
        
        # (SỬA) Dùng hằng số PORT từ common/constants (mặc định 13000)
        if self.network.connect(ip, 13000): 
            self.network.send_message(f"LOGIN:{self.username}") # Protocol mới
            self.root.after(100, self.process_messages) # Bắt đầu vòng lặp
            self.show_waiting_screen()
        else:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến {ip}:13000.")

    # ---------- Màn chờ ----------
    def show_waiting_screen(self):
        self.clear_main_frame()
        self.waiting_frame = ttk.Frame(self.main_frame)
        self.waiting_frame.pack(expand=True)
        ttk.Label(self.waiting_frame, text="Đang tìm đối thủ...", font=("Arial", 18)).pack()
        progress = ttk.Progressbar(self.waiting_frame, mode='indeterminate')
        progress.pack(pady=20, padx=50, fill=tk.X)
        progress.start()

    # ---------- Giao diện chính (Vẽ bàn cờ) ----------
    def setup_game_view(self):
        self.clear_main_frame()
        container = ttk.Frame(self.main_frame)
        container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # (QUAN TRỌNG) Tạo self.status_bar
        self.status_bar = ttk.Label(container, text="...", font=("Arial", 14, "italic"), anchor=tk.CENTER)
        self.status_bar.pack(pady=(0, 10), fill=tk.X)

        info = ttk.Frame(container)
        info.pack(fill=tk.X, pady=(0,6))
        self.you_label = ttk.Label(info, text=f"Bạn: {self.username}", font=("Arial", 11))
        self.vs_label = ttk.Label(info, text="VS", font=("Arial", 11, "bold"))
        self.opponent_label = ttk.Label(info, text=f"Đối thủ: {self.opponent_name}", font=("Arial", 11))
        self.you_label.pack(side=tk.LEFT, padx=10)
        self.vs_label.pack(side=tk.LEFT, padx=6)
        self.opponent_label.pack(side=tk.LEFT, padx=6)

        self.game_board = GameBoardUI(container, size=25, cell_size=28)
        self.game_board.move_callback = self.on_board_click

    # ---------- Xử lý nước đi ----------
    def on_board_click(self, row, col):
        if self.game.board[row][col] != 0: return

        if self.game_started:  # Chế độ Online
            if self.my_turn:
                self.network.send_message(f"MOVE:{row},{col}")
                self.game.make_move(row, col, self.my_piece_id)
                self.game_board.place_piece(row, col, self.my_piece_id)
                winner, line = self.game.check_win_and_get_line(row, col)
                if winner:
                    self.game_board.draw_winning_line(line[0], line[1])
                    self.handle_game_result("Bạn đã chiến thắng!")
                    self.network.send_message("WIN")
                    return
                self.my_turn = False
                self.stop_timer()
                self.status_bar.config(text="Đang chờ đối thủ...")
        else: # Chế độ Offline (game_started là False)
            if self.my_turn:
                self.my_turn = False
                self.handle_click_offline(row, col)

    def handle_click_offline(self, row, col):
        # Người chơi đi (Luôn là quân 1 - O)
        self.game.make_move(row, col, 1)
        self.game_board.place_piece(row, col, 1)
        winner, line = self.game.check_win_and_get_line(row, col)
        if winner:
            self.game_board.draw_winning_line(line[0], line[1])
            self.handle_game_result_offline(winner)
            return

        self.status_bar.config(text="Máy đang suy nghĩ...")
        self.root.after(500, self.execute_ai_turn) # Gọi AI sau 0.5s

    def execute_ai_turn(self):
        # (SỬA) Gọi hàm điều phối AI mới
        # Hàm này sẽ tự chọn logic "easy" hoặc "hard"
        
        # Máy luôn là quân 2 (X)
        ai_row, ai_col = ai.find_best_move(self.game.board, 2, self.difficulty)
            
        # Thực hiện nước đi của AI
        self.game.make_move(ai_row, ai_col, 2)
        self.game_board.place_piece(ai_row, ai_col, 2)
        
        winner, line = self.game.check_win_and_get_line(ai_row, ai_col)
        if winner:
            self.game_board.draw_winning_line(line[0], line[1])
            self.handle_game_result_offline(winner)
        else:
            self.status_bar.config(text="Tới lượt bạn.")
            self.my_turn = True

    # ---------- Xử lý message từ server (Dùng protocol mới) ----------
    def process_messages(self):
        try:
            while not self.message_queue.empty():
                msg = self.message_queue.get_nowait()
                
                try:
                    parts = msg.split(':')
                    cmd = parts[0]

                    if cmd == "LOGIN_OK":
                        pass # Đăng nhập thành công, chờ server...
                    elif cmd == "LOGIN_FAIL":
                        messagebox.showerror("Lỗi", f"Đăng nhập thất bại: {parts[1]}")
                    elif cmd == "WAITING":
                        pass # Vẫn đang chờ...
                    elif cmd == "MATCH": 
                        data = parts[1].split(',')
                        self.opponent_name = data[0]
                        self.my_piece_id = int(data[1])
                        self.game_started = True # Bật cờ Online
                        
                        self.setup_game_view() # VẼ BÀN CỜ
                        
                        my_piece_str = "O (Đi trước)" if self.my_piece_id == 1 else "X (Đi sau)"
                        self.you_label.config(text=f"Bạn: {self.username} ({my_piece_str})")
                        self.opponent_label.config(text=f"Đối thủ: {self.opponent_name}")
                        messagebox.showinfo("Bắt đầu!", f"Bạn là quân {my_piece_str}.")

                    elif cmd == "START":
                        pass # Không cần làm gì, MATCH đã xử lý
                    elif cmd == "TURN": 
                        self.my_turn = True
                        self.status_bar.config(text="Tới lượt bạn!")
                        # self.start_timer(30) # (Bật timer nếu muốn)
                    elif cmd == "OP_MOVE": 
                        row, col = map(int, parts[1].split(','))
                        opponent_piece_id = 2 if self.my_piece_id == 1 else 1
                        if self.game.board[row][col] == 0:
                            self.game.make_move(row, col, opponent_piece_id)
                            self.game_board.place_piece(row, col, opponent_piece_id)
                            winner, line = self.game.check_win_and_get_line(row, col)
                            if winner:
                                self.game_board.draw_winning_line(line[0], line[1])
                    elif cmd == "OP_WIN":
                        self.handle_game_result("Bạn đã thua!")
                    elif cmd == "OP_LEFT":
                        self.handle_game_result("Đối thủ đã thoát!")
                    elif cmd == "CONNECTION_LOST":
                        messagebox.showerror("Mất kết nối", "Mất kết nối tới server.")
                        self.root.quit()
                
                except Exception as e:
                    print(f"LỖI: Không thể xử lý message: '{msg}'. Lỗi: {e}")
                    traceback.print_exc()

        finally:
            self.root.after(100, self.process_messages) # Đảm bảo vòng lặp luôn chạy lại

    # ---------- Timer ----------
    def start_timer(self, t):
        self.stop_timer()
        self.remaining_time = t
        self.update_timer()

    def update_timer(self):
        if self.my_turn and self.remaining_time > 0:
            self.status_bar.config(text=f"Tới lượt bạn! Còn {self.remaining_time}s.")
            self.remaining_time -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        elif self.my_turn and self.remaining_time <= 0:
            self.my_turn = False
            self.status_bar.config(text="Hết giờ!")

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    # ---------- Kết thúc ----------
    def handle_game_result(self, text):
        self.my_turn = False
        self.game_started = False
        self.stop_timer()
        messagebox.showinfo("Kết thúc", text)
        self.root.quit() # Tạm thời đóng game

    def handle_game_result_offline(self, winner):
        msg = "Chúc mừng, bạn đã thắng!" if winner == 'O won' else "Máy đã thắng!"
        messagebox.showinfo("Kết thúc", msg)
        if messagebox.askyesno("Chơi lại?", "Chơi lại không?"):
            self.game.reset_board()
            self.game_board.reset()
            self.status_bar.config(text="Tới lượt bạn.")
            self.my_turn = True
        else:
            self.root.quit() # Tạm thời đóng game

    def clear_main_frame(self):
        for w in self.main_frame.winfo_children():
            w.destroy()