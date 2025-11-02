# client/main.py
import sys
import os
import tkinter as tk

# --- BẮT ĐẦU DEBUG ---
print(f"--- [DEBUG] Bắt đầu client/main.py ---")
print(f"--- [DEBUG] __file__ = {__file__}")
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"--- [DEBUG] SCRIPT_DIR = {SCRIPT_DIR}")
    
    # Lấy đường dẫn đến thư mục gốc của dự án (là thư mục cha của 'client')
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    print(f"--- [DEBUG] PROJECT_ROOT = {PROJECT_ROOT}")
    
    # Thêm thư mục gốc (chứa 'common', 'client', 'server') vào sys.path
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
        print(f"--- [DEBUG] ĐÃ THÊM {PROJECT_ROOT} vào sys.path")
except Exception as e:
    print(f"--- [DEBUG] LỖI khi xử lý sys.path: {e}")
# --- KẾT THÚC DEBUG ---

print(f"--- [DEBUG] sys.path hiện tại (5 dòng đầu):")
for i, path in enumerate(sys.path[:5]):
    print(f"--- [DEBUG]   {i}: {path}")

print(f"--- [DEBUG] Đang thử import 'client.ui.login_ui'...")
from client.ui.login_ui import LoginUI
print(f"--- [DEBUG] Import 'client.ui.login_ui' THÀNH CÔNG.")
print(f"--- [DEBUG] Đang thử import 'client.ui.game_ui'...")
from client.ui.game_ui import ChessboardApp
print(f"--- [DEBUG] Import 'client.ui.game_ui' THÀNH CÔNG.")


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Caro Online")
        self.show_login()

    def show_login(self):
        self.login_ui = LoginUI(self.root, self.on_login_success)

    def on_login_success(self, username, mode, difficulty):
        self.login_ui.frame.destroy()  
        
        app = ChessboardApp(self.root, username=username, mode=mode, difficulty=difficulty)
        
        if mode == "online":
            app.show_login_ui()
        else: # mode == "offline"
            app.start_offline_game()

if __name__ == "__main__":
    root = tk.Tk()
    MainApp(root)
    root.mainloop()