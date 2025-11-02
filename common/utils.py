# common/utils.py
import datetime

def save_match_history(player1, player2, winner):
    """Ghi lịch sử trận đấu vào file."""
    try:
        with open("match_history.log", "a", encoding="utf-8") as f:
            log_entry = f"{datetime.datetime.now()}: {player1} vs {player2} -> Winner: {winner}\n"
            f.write(log_entry)
            print(log_entry.strip())
    except Exception as e:
        print(f"Error saving match history: {e}")