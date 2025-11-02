# client/logic/ai.py
import random
import math

# --- Định nghĩa hằng số ---
BOARD_SIZE = 25
AI_PIECE = 2        # Máy (X)
PLAYER_PIECE = 1    # Người (O)
EMPTY = 0
WINNING_LENGTH = 5 # 5 quân để thắng

# --- HÀM ĐIỀU PHỐI (Router) ---
def find_best_move(board, piece_id, difficulty):
    """
    Đây là hàm chính mà game_ui.py sẽ gọi.
    Nó sẽ chọn logic AI dựa trên độ khó.
    """
    if difficulty == "easy":
        return get_easy_move(board, piece_max_piece=piece_id)
    
    # --- LOGIC "KHÓ" (Đại học) ĐÃ TỐI ƯU ---
    opponent_piece = PLAYER_PIECE if piece_id == AI_PIECE else AI_PIECE

    # 1. (Ưu tiên) Thắng ngay
    move = find_threat_move(board, piece_id, WINNING_LENGTH - 1)
    if move:
        return move

    # 2. (Ưu tiên) Chặn đối thủ thắng ngay
    move = find_threat_move(board, opponent_piece, WINNING_LENGTH - 1)
    if move:
        return move

    # 3. Xử lý các nước đi đầu tiên (khi Minimax không cần thiết/quá chậm)
    first_move = get_first_move(board) 
    if first_move:
        return first_move # Đánh ở giữa hoặc bên cạnh
    
    # 4. Bàn cờ đã có nhiều nước, chạy Minimax
    # (depth=2 là đủ nhanh và mạnh với 'get_relevant_moves')
    _, move = minimax(board, depth=2, alpha=-math.inf, beta=math.inf, maximizing_player=True, ai_piece=piece_id)
    
    if move:
        return move
    else:
        # Failsafe: Nếu minimax (vì lý do nào đó) không trả về gì
        # (ví dụ: không còn nước đi 'relevant')
        return get_easy_move(board, piece_id) # Dùng AI Dễ làm dự phòng

# -----------------------------------------------
# --- LOGIC AI "DỄ" (Học sinh Cấp 1) ---
# -----------------------------------------------

def get_easy_move(board, piece_max_piece):
    """
    Logic AI Cấp 1:
    1. Tìm nước đi để THẮNG NGAY LẬP TỨC (5-in-a-row).
    2. Tìm nước đi để CHẶN ĐỐI THỦ THẮNG.
    3. Tìm nước đi để CHẶN ĐỐI THỦ tạo 4 nước (hở 1 đầu).
    4. Tìm nước đi để CHẶN ĐỐI THỦ tạo 3 nước (hở 2 đầu).
    5. Nếu không, đánh gần một quân cờ bất kỳ (để học chơi).
    6. Nếu bàn cờ trống, đánh ở giữa.
    """
    piece_id = AI_PIECE # AI luôn là quân 2
    opponent_piece = PLAYER_PIECE

    # 1. Thắng ngay
    move = find_threat_move(board, piece_id, WINNING_LENGTH - 1)
    if move:
        return move

    # 2. Chặn đối thủ thắng ngay
    move = find_threat_move(board, opponent_piece, WINNING_LENGTH - 1)
    if move:
        return move

    # 3. Chặn đối thủ tạo 4 nước (hở 1)
    move = find_threat_move(board, opponent_piece, WINNING_LENGTH - 2, open_ends=1)
    if move:
        return move
        
    # 4. Chặn đối thủ tạo 3 nước (hở 2)
    move = find_threat_move(board, opponent_piece, WINNING_LENGTH - 3, open_ends=2)
    if move:
        return move

    # 5. Đánh gần một quân cờ bất kỳ
    move = find_move_near_piece(board)
    if move:
        return move

    # 6. Đánh ở giữa (nếu các bước trên thất bại)
    if board[BOARD_SIZE // 2][BOARD_SIZE // 2] == EMPTY:
        return (BOARD_SIZE // 2, BOARD_SIZE // 2)

    # 7. Failsafe: Nước đi ngẫu nhiên (hiếm khi xảy ra)
    return get_random_move(board)

def find_threat_move(board, piece_id, threat_length, open_ends=1):
    """Hàm helper cho AI 'Dễ': Tìm 1 nước đi để tạo/chặn 1 hàng 'threat_length'"""
    empty_cells = get_valid_locations(board) # Lấy tất cả ô trống
    
    for r, c in empty_cells:
        board[r][c] = piece_id # Đặt thử
        
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            count = 0
            ends = 0
            
            # Đếm 1 hướng
            for i in range(1, WINNING_LENGTH):
                nr, nc = r + i*dr, c + i*dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == piece_id:
                    count += 1
                else:
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                        ends += 1
                    break
            
            # Đếm hướng ngược lại
            for i in range(1, WINNING_LENGTH):
                nr, nc = r - i*dr, c - i*dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == piece_id:
                    count += 1
                else:
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                        ends += 1
                    break
            
            board[r][c] = EMPTY # Hoàn tác
            
            if count >= threat_length and ends >= open_ends:
                return (r, c)
                
        board[r][c] = EMPTY # Hoàn tác (quan trọng)
    return None

def find_move_near_piece(board):
    """Hàm helper cho AI 'Dễ': Tìm ô trống bất kỳ bên cạnh 1 quân cờ đã đánh"""
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == EMPTY:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] != EMPTY:
                            return (r, c)
    return None

def get_random_move(board):
    """Hàm helper: Lấy 1 nước đi ngẫu nhiên"""
    empty_cells = get_valid_locations(board)
    if empty_cells:
        return random.choice(empty_cells)
    return (0, 0) # Không còn nước


# -----------------------------------------------
# --- LOGIC AI "KHÓ" (Đại học - Minimax) ---
# -----------------------------------------------

def get_first_move(board):
    """(TỐI ƯU MỚI) Xử lý 1-2 nước đi đầu tiên"""
    player_moves = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == PLAYER_PIECE:
                player_moves.append((r,c))

    # 1. Bàn cờ trống (AI đi trước - hiếm)
    if not player_moves:
        return (BOARD_SIZE // 2, BOARD_SIZE // 2) # Đánh giữa

    # 2. Người chơi mới đánh 1 nước
    if len(player_moves) == 1:
        # Đánh ngay bên cạnh nước đi của người chơi
        r, c = player_moves[0]
        # Ưu tiên đánh chéo (khó chịu hơn)
        if 0 <= r+1 < BOARD_SIZE and 0 <= c+1 < BOARD_SIZE and board[r+1][c+1] == EMPTY:
            return (r+1, c+1)
        elif 0 <= r+1 < BOARD_SIZE and board[r+1][c] == EMPTY:
            return (r+1, c)
        else: # Đánh bên trên
            return (r-1, c)
    
    return None # Bàn cờ đã có nhiều nước, hãy dùng Minimax

def get_relevant_moves(board):
    """
    (TỐI ƯU MỚI) Hàm quan trọng nhất!
    Chỉ tìm các ô trống "có liên quan".
    """
    relevant_moves = set()
    # (SỬA LỖI LAG) Giảm bán kính tìm kiếm xuống 1 (chỉ 8 ô 3x3 xung quanh)
    search_radius = 1 

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY: # Nếu ô này CÓ CỜ
                # Thêm các ô trống xung quanh nó vào 'relevant_moves'
                for dr in range(-search_radius, search_radius + 1):
                    for dc in range(-search_radius, search_radius + 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                            relevant_moves.add((nr, nc))
                            
    if not relevant_moves: # Nếu không tìm thấy (ví dụ: bàn cờ trống)
        return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
        
    return list(relevant_moves)

def get_valid_locations(board):
    """Lấy danh sách tất cả các ô trống (Dùng cho AI Dễ)"""
    locations = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == EMPTY:
                locations.append((r, c))
    return locations

def is_terminal_node(board):
    """Kiểm tra xem game đã kết thúc chưa (có ai thắng hoặc hòa)"""
    return check_win(board, PLAYER_PIECE) or check_win(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def check_win(board, piece_id):
    """Kiểm tra thắng (đơn giản)"""
    # Ngang
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE - (WINNING_LENGTH - 1)):
            if all(board[r][c+i] == piece_id for i in range(WINNING_LENGTH)):
                return True
    # Dọc
    for c in range(BOARD_SIZE):
        for r in range(BOARD_SIZE - (WINNING_LENGTH - 1)):
            if all(board[r+i][c] == piece_id for i in range(WINNING_LENGTH)):
                return True
    # Chéo (xuống)
    for c in range(BOARD_SIZE - (WINNING_LENGTH - 1)):
        for r in range(BOARD_SIZE - (WINNING_LENGTH - 1)):
            if all(board[r+i][c+i] == piece_id for i in range(WINNING_LENGTH)):
                return True
    # Chéo (lên)
    for c in range(BOARD_SIZE - (WINNING_LENGTH - 1)):
        for r in range(WINNING_LENGTH - 1, BOARD_SIZE):
            if all(board[r-i][c+i] == piece_id for i in range(WINNING_LENGTH)):
                return True
    return False

def evaluate_window(window, piece_id):
    """Hàm helper: Tính điểm cho một "cửa sổ" 5 ô"""
    score = 0
    opponent_piece = PLAYER_PIECE if piece_id == AI_PIECE else AI_PIECE

    if window.count(piece_id) == 5:
        score += 1000000 # Thắng
    elif window.count(piece_id) == 4 and window.count(EMPTY) == 1:
        score += 5000 # 4 hở 1
    elif window.count(piece_id) == 3 and window.count(EMPTY) == 2:
        score += 500 # 3 hở 2
    
    # Điểm phòng thủ (quan trọng hơn tấn công 1 chút)
    if window.count(opponent_piece) == 4 and window.count(EMPTY) == 1:
        score -= 7000 # Chặn 4 hở 1 (ưu tiên cao)
    elif window.count(opponent_piece) == 3 and window.count(EMPTY) == 2:
        score -= 700 # Chặn 3 hở 2

    return score

def score_board(board, piece_id):
    """Tính tổng điểm của bàn cờ cho AI"""
    score = 0
    
    # Ưu tiên trung tâm
    center_array = [board[r][BOARD_SIZE//2] for r in range(BOARD_SIZE)]
    score += center_array.count(piece_id) * 3

    # Tính điểm Ngang
    for r in range(BOARD_SIZE):
        row_array = [board[r][c] for c in range(BOARD_SIZE)]
        for c in range(BOARD_SIZE - WINNING_LENGTH + 1):
            window = row_array[c:c+WINNING_LENGTH]
            score += evaluate_window(window, piece_id)

    # Tính điểm Dọc
    for c in range(BOARD_SIZE):
        col_array = [board[r][c] for r in range(BOARD_SIZE)]
        for r in range(BOARD_SIZE - WINNING_LENGTH + 1):
            window = col_array[r:r+WINNING_LENGTH]
            score += evaluate_window(window, piece_id)

    # Tính điểm Chéo (xuống)
    for r in range(BOARD_SIZE - WINNING_LENGTH + 1):
        for c in range(BOARD_SIZE - WINNING_LENGTH + 1):
            window = [board[r+i][c+i] for i in range(WINNING_LENGTH)]
            score += evaluate_window(window, piece_id)

    # Tính điểm Chéo (lên)
    for r in range(WINNING_LENGTH - 1, BOARD_SIZE):
        for c in range(BOARD_SIZE - WINNING_LENGTH + 1):
            window = [board[r-i][c+i] for i in range(WINNING_LENGTH)]
            score += evaluate_window(window, piece_id)

    return score

def minimax(board, depth, alpha, beta, maximizing_player, ai_piece):
    """Thuật toán Minimax với Alpha-Beta Pruning (Đại học)"""
    
    player_piece = PLAYER_PIECE if ai_piece == AI_PIECE else AI_PIECE
    
    # (SỬA LỖI TỐI ƯU)
    # Chỉ tìm các nước đi "liên quan", không tìm tất cả 600+ ô
    valid_locations = get_relevant_moves(board) 
    
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if check_win(board, ai_piece):
                return (1000000000, None)
            elif check_win(board, player_piece):
                return (-1000000000, None)
            else: # Hòa
                return (0, None)
        else: # Hết độ sâu (depth == 0)
            return (score_board(board, ai_piece), None)

    if not valid_locations: # Nếu không còn nước đi "relevant"
         return (0, None) # Hòa

    if maximizing_player: # Lượt của AI (Max)
        best_score = -math.inf
        best_move = random.choice(valid_locations) # Khởi tạo
        
        for r, c in valid_locations: # Vòng lặp này giờ đã rất nhanh
            board[r][c] = ai_piece
            score, _ = minimax(board, depth - 1, alpha, beta, False, ai_piece)
            board[r][c] = EMPTY # Hoàn tác
            
            if score > best_score:
                best_score = score
                best_move = (r, c)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score, best_move

    else: # Lượt của Người (Min)
        best_score = math.inf
        best_move = random.choice(valid_locations)
        
        for r, c in valid_locations: # Vòng lặp này giờ đã rất nhanh
            board[r][c] = player_piece
            score, _ = minimax(board, depth - 1, alpha, beta, True, ai_piece)
            board[r][c] = EMPTY # Hoàn tác
            
            if score < best_score:
                best_score = score
                best_move = (r, c)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move