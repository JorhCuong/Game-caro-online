# common/protocol.py
# Định nghĩa các quy tắc giao tiếp (protocol)

# Client -> Server
MSG_LOGIN = "LOGIN"       # Định dạng: "LOGIN:username"
MSG_MOVE = "MOVE"         # Định dạng: "MOVE:y,x"
MSG_WIN = "WIN"           # Định dạng: "WIN"
MSG_DRAW = "DRAW"         # Định dạng: "DRAW"
MSG_REPLAY = "REPLAY"     # Định dạng: "REPLAY"

# Server -> Client
MSG_LOGIN_SUCCESS = "LOGIN_OK"  # Định dạng: "LOGIN_OK"
MSG_LOGIN_FAIL = "LOGIN_FAIL"   # Định dạng: "LOGIN_FAIL:reason"
MSG_WAITING = "WAITING"       # Định dạng: "WAITING"
MSG_MATCH = "MATCH"         # Định dạng: "MATCH:opponent_name,your_piece_id" (vd: "MATCH:Player2,1")
MSG_OPPONENT_MOVE = "OP_MOVE" # Định dạng: "OP_MOVE:y,x"
MSG_OPPONENT_WIN = "OP_WIN"   # Định dạng: "OP_WIN"
MSG_OPPONENT_DRAW = "OP_DRAW" # Định dạng: "OP_DRAW"
MSG_GAME_START = "START"      # Định dạng: "START"
MSG_YOUR_TURN = "TURN"        # Định dạng: "TURN"
MSG_OPPONENT_LEFT = "OP_LEFT" # Định dạng: "OP_LEFT"
MSG_TIMEOUT = "TIMEOUT"       # Định dạng: "TIMEOUT"