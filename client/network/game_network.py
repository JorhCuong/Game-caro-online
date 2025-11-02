import socket
import threading
import queue

class NetworkManager:
    def __init__(self, message_queue):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_queue = message_queue # Dùng queue để giao tiếp an toàn giữa các thread
        self.buffer = ""

    def connect(self, host, port):
        try:
            self.client.connect((host, port))
            # Bắt đầu một thread để lắng nghe tin nhắn từ server
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True # Thread sẽ tự tắt khi chương trình chính kết thúc
            receive_thread.start()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send_message(self, message):
        try:
            if not message.endswith('\n'):
                message += '\n'
            self.client.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")

    def receive_messages(self):
        self.buffer = ""
        while True:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if not data:
                    raise ConnectionResetError("Server closed connection")
                
                self.buffer += data
                
                # Xử lý buffer, tìm các message hoàn chỉnh (kết thúc bằng \n)
                while '\n' in self.buffer:
                    # Tách message đầu tiên ra khỏi buffer
                    message, self.buffer = self.buffer.split('\n', 1)
                    if message: # Không xử lý message rỗng
                        self.message_queue.put(message)
                        
            except ConnectionResetError as e:
                print(f"Lost connection to server: {e}")
                self.message_queue.put("CONNECTION_LOST")
                break
            except Exception as e:
                print(f"Error in receive_messages: {e}")
                self.message_queue.put("CONNECTION_LOST")
                break