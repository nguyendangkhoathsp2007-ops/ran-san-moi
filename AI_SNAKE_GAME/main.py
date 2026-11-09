"""
main.py - Điểm khởi chạy chính của dự án Game AI Snake
Phát triển bởi lập trình viên Python & Chuyên gia AI.
Thuật toán: A* Pathfinding phối hợp Hamiltonian Cycle Shortcutting.
"""

import sys
import os

# Đảm bảo thư mục hiện tại nằm trong sys.path để import dễ dàng trong mọi IDE (VS Code, PyCharm, Terminal)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from game import Game


def main():
    print("=" * 60)
    print("      KHỞI CHẠY GAME AI SNAKE - A* & HAMILTONIAN CYCLE     ")
    print("=" * 60)
    print("  [Space]       : Tạm dừng / Tiếp tục")
    print("  [R]           : Khởi động lại (Restart)")
    print("  [Up / Right]  : Tăng tốc độ")
    print("  [Down / Left] : Giảm tốc độ")
    print("  [P]           : Bật / Tắt hiển thị đường đi A*")
    print("  [S]           : Bật / Tắt hiển thị ô tìm kiếm A*")
    print("  [H]           : Bật / Tắt hiển thị Chu trình Hamiltonian")
    print("  [M]           : Chuyển đổi chế độ AI (Hybrid / Pure / A*)")
    print("=" * 60)

    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\nĐã nhận tín hiệu dừng từ người dùng. Thoát game thành công.")
    except Exception as e:
        print(f"\n[Lỗi ngoại lệ]: {e}")
        raise


if __name__ == "__main__":
    main()
