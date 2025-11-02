# login.py (Phiên bản Gỗ/Giấy - Có 2 nút - Đã sửa lỗi)
import tkinter as tk
from tkinter import ttk
import os

class LoginUI:
    def __init__(self, root, on_login_callback):
        self.root = root
        self.on_login_callback = on_login_callback

        # ======= Bảng màu (Theme) =======
        self.BG_COLOR = "#fefaf5"       # Màu nền giấy
        self.CARD_COLOR = "#fdf6e3"     # Màu thẻ
        self.TITLE_COLOR = "#654321"    # Màu nâu đậm
        self.TEXT_COLOR = "#58452d"     # Màu chữ
        self.BUTTON_COLOR = "#a07a48"   # Màu gỗ/nút
        self.BUTTON_ACTIVE = "#654321"
        self.WHITE = "#FFFFFF"
        self.ERROR_COLOR = "#e63946"
        self.SUCCESS_COLOR = "#2a9d8f"

        # ======= Kích thước cửa sổ =======
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.window_width = int(screen_height * 0.95)
        self.window_height = screen_height
        self.center_window(screen_width, screen_height)

        self.root.resizable(False, False)

        self.selected_mode = "online" # Mặc định

        self.x_image = None
        self.o_image = None
        self.load_assets()

        # ======= (QUAN TRỌNG) Đặt tên là 'self.frame' =======
        # Giữ tên 'self.frame' để client_main.py có thể .destroy()
        self.frame = tk.Canvas(self.root, width=self.window_width, height=self.window_height, highlightthickness=0)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # ======= Style cho các widget =======
        self.setup_styles()

        # ======= Card Đăng nhập (đặt trên Canvas) =======
        self.card_frame = ttk.Frame(
            self.frame, # Gắn vào self.frame (canvas)
            style="Card.TFrame",
            padding=(60, 40, 60, 60)
        )
        # Tạo self.card_window TRƯỚC
        self.card_window = self.frame.create_window(
            self.window_width / 2, self.window_height / 2, 
            window=self.card_frame, 
            anchor=tk.CENTER
        )
        
        # Gọi hàm vẽ nền SAU KHI self.card_window đã tồn tại
        self.draw_background()

        # ======= Tiêu đề =======
        title_frame = ttk.Frame(self.card_frame, style="Card.TFrame")
        title_frame.pack(pady=(10, 40))

        if self.o_image:
            ttk.Label(title_frame, image=self.o_image, style="Card.TLabel").pack(side=tk.LEFT, padx=20)
        ttk.Label(
            title_frame,
            text="GAME CỜ CARO",
            style="Title.TLabel"
        ).pack(side=tk.LEFT)
        if self.x_image:
            ttk.Label(title_frame, image=self.x_image, style="Card.TLabel").pack(side=tk.LEFT, padx=20)

        # ======= Ô nhập tên =======
        ttk.Label(
            self.card_frame,
            text="Bạn tên là gì?",
            style="Text.TLabel"
        ).pack(pady=(10, 5))
        self.name_entry = ttk.Entry(
            self.card_frame,
            font=("Arial", 16),
            width=30,
            justify=tk.CENTER,
            style="Custom.TEntry"
        )
        self.name_entry.pack(pady=10, ipady=8)
        self.name_entry.focus()
        self.name_entry.bind("<Return>", self.on_play_click_event)

        self.selected_difficulty = "hard" # Mac dinh la "Kho"
        self.create_difficulty_buttons(self.card_frame)
        self.difficulty_frame.pack_forget() # An di luc bat dau

        # ======= Nút Bắt Đầu =======
        self.play_button = ttk.Button(
            self.card_frame,
            text="Bắt Đầu",
            style="Accent.TButton",
            command=self.on_play_click
        )
        self.play_button.pack(pady=(25, 10), ipadx=25, ipady=12)

        # ======= Frame chọn chế độ (dùng Nút bấm) =======
        mode_button_frame = ttk.Frame(self.card_frame, style="Card.TFrame")
        mode_button_frame.pack(pady=(15, 10), fill=tk.X, padx=30) 

        self.online_button = ttk.Button(
            mode_button_frame,
            text="👤  Chơi với người",
            style="ModeButtonActive.TButton",
            command=self.select_online
        )
        self.online_button.pack(fill=tk.X, ipady=7, pady=(0, 6)) 

        self.offline_button = ttk.Button(
            mode_button_frame,
            text="🤖  Chơi với máy",
            style="ModeButton.TButton",
            command=self.select_offline
        )
        self.offline_button.pack(fill=tk.X, ipady=7)

        # ======= Thông báo =======
        self.message_label = ttk.Label(
            self.card_frame,
            text="",
            style="Message.TLabel"
        )
        self.message_label.pack(pady=(20, 10))

        self.frame.bind("<Configure>", self.on_canvas_resize)

    def draw_background(self):
        """Vẽ nền Gỗ/Giấy."""
        self.frame.delete("background") 
        self.frame.config(bg=self.BUTTON_COLOR) 
        margin = 20
        self.frame.create_rectangle(
            margin, margin,
            self.window_width - margin,
            self.window_height - margin,
            fill=self.BG_COLOR,
            outline="",
            tags="background"
        )
        self.frame.tag_raise(self.card_window)

    def load_assets(self):
        """Tải ảnh X và O."""
        try:
            base_assets = os.path.join(os.getcwd(), "assets")
            x_path = os.path.join(base_assets, "x.png")
            o_path = os.path.join(base_assets, "o.png")
            
            if os.path.exists(x_path):
                self.x_image = tk.PhotoImage(file=x_path) 
            if os.path.exists(o_path):
                self.o_image = tk.PhotoImage(file=o_path)
            
            print("Đã tải assets (X, O).")
        except Exception as e:
            print(f"Lỗi khi tải assets: {e}")
            pass

    def on_canvas_resize(self, event):
        self.window_width = event.width
        self.window_height = event.height
        self.draw_background() 
        self.frame.coords(self.card_window, self.window_width / 2, self.window_height / 2)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Card.TFrame", background=self.CARD_COLOR, borderwidth=2, relief="solid", bordercolor=self.BUTTON_COLOR)
        style.configure("Card.TLabel", background=self.CARD_COLOR)
        style.configure("Title.TLabel", font=("Arial", 44, "bold"), foreground=self.TITLE_COLOR, background=self.CARD_COLOR)
        style.configure("Text.TLabel", font=("Arial", 16), foreground=self.TEXT_COLOR, background=self.CARD_COLOR)
        style.configure("Message.TLabel", font=("Arial", 13, "italic"), background=self.CARD_COLOR)
        style.configure("Custom.TEntry", bordercolor=self.BUTTON_COLOR, lightcolor=self.BUTTON_COLOR, fieldbackground=self.BG_COLOR, foreground=self.TEXT_COLOR, insertcolor=self.TEXT_COLOR)
        style.configure("Accent.TButton", font=("Arial", 16, "bold"), padding=10, background=self.BUTTON_COLOR, foreground=self.WHITE, borderwidth=0, relief="flat")
        style.map("Accent.TButton", background=[('active', self.BUTTON_ACTIVE)], foreground=[('active', 'white')])
        style.configure("ModeButton.TButton", font=("Arial", 14), padding=10, background=self.CARD_COLOR, foreground=self.BUTTON_COLOR, borderwidth=2, relief="solid", bordercolor=self.BUTTON_COLOR)
        style.map("ModeButton.TButton", background=[('active', self.BG_COLOR)], foreground=[('active', self.BUTTON_ACTIVE)])
        style.configure("ModeButtonActive.TButton", font=("Arial", 14), padding=10, background=self.BUTTON_COLOR, foreground=self.WHITE, borderwidth=2, relief="solid", bordercolor=self.BUTTON_COLOR)
        style.map("ModeButtonActive.TButton", background=[('active', self.BUTTON_ACTIVE)], foreground=[('active', self.WHITE)])

    def select_online(self):
        self.selected_mode = "online"
        self.online_button.config(style="ModeButtonActive.TButton")
        self.offline_button.config(style="ModeButton.TButton")
        self.difficulty_frame.pack_forget() # AN di khi chon Online

    def select_offline(self):
        self.selected_mode = "offline"
        self.offline_button.config(style="ModeButtonActive.TButton")
        self.online_button.config(style="ModeButton.TButton")
        self.difficulty_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

    def center_window(self, screen_width, screen_height):
        x = int((screen_width / 2) - (self.window_width / 2))
        y = 0
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def on_play_click(self):
        username = self.name_entry.get().strip()
        if not username:
            self.message_label.config(text="⚠️ Vui lòng nhập tên!", foreground=self.ERROR_COLOR)
            return
        
        self.play_button.config(state=tk.DISABLED, text="Đang xử lý...")
        self.name_entry.config(state=tk.DISABLED)
        self.online_button.config(state=tk.DISABLED)
        self.offline_button.config(state=tk.DISABLED)
        
        selected_mode = self.selected_mode 
        selected_mode_text = "Chơi với người" if selected_mode == "online" else "Chơi với máy"
        
        self.message_label.config(
            text=f"Xin chào, {username}! Vào chế độ: {selected_mode_text}...",
            foreground=self.SUCCESS_COLOR
        )
        
        if self.on_login_callback:
            # Gửi cả username và selected_mode
            self.root.after(1000, lambda: self.on_login_callback(username, self.selected_mode, self.selected_difficulty))

    def on_play_click_event(self, event=None):
        if self.play_button['state'] == tk.NORMAL:
            self.on_play_click()

    # (Them 3 ham moi nay vao class LoginUI)

    def create_difficulty_buttons(self, parent):
        """Tao cac nut chon do kho"""
        self.difficulty_frame = tk.Frame(parent, bg=self.CARD_COLOR)
        
        ttk.Label(
            self.difficulty_frame,
            text="CHỌN ĐỘ KHÓ",
            style="SmallTitle.TLabel"
        ).pack(pady=(10, 5))

        self.easy_button = ttk.Button(
            self.difficulty_frame,
            text="Dễ",
            style="ModeButton.TButton",
            command=self.select_easy
        )
        self.easy_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 5))

        self.hard_button = ttk.Button(
            self.difficulty_frame,
            text="Khó",
            style="ModeButtonActive.TButton", # Mac dinh chon "Kho"
            command=self.select_hard
        )
        self.hard_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 20))
        
        # Gan vao parent
        self.difficulty_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

    def select_easy(self):
        """Khi chon che do De"""
        self.selected_difficulty = "easy"
        self.easy_button.config(style="ModeButtonActive.TButton")
        self.hard_button.config(style="ModeButton.TButton")

    def select_hard(self):
        """Khi chon che do Kho"""
        self.selected_difficulty = "hard"
        self.hard_button.config(style="ModeButtonActive.TButton")
        self.easy_button.config(style="ModeButton.TButton")