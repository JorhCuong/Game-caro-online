# server/main.py
import sys
import os

# --- BẮT ĐẦU DEBUG ---
print(f"--- [DEBUG] Bắt đầu server/main.py ---")
print(f"--- [DEBUG] __file__ = {__file__}")
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"--- [DEBUG] SCRIPT_DIR = {SCRIPT_DIR}")
    
    # Lấy đường dẫn đến thư mục gốc của dự án (là thư mục cha của 'server')
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

print(f"--- [DEBUG] Đang thử import 'common.constants'...")
from common.constants import HOST, PORT
print(f"--- [DEBUG] Import 'common.constants' THÀNH CÔNG.")

print(f"--- [DEBUG] Đang thử import 'server.server'...")
from server.server import Server
print(f"--- [DEBUG] Import 'server.server' THÀNH CÔNG.")


def main():
    print(f"\n--- [LOG] Starting server on {HOST}:{PORT} ---")
    server = Server(HOST, PORT)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n--- [LOG] Server is shutting down... ---")
        server.stop()
    except Exception as e:
        print(f"--- [LOG] An unexpected error occurred: {e} ---")
        server.stop()

if __name__ == "__main__":
    main()