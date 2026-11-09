"""
settings.py - Cấu hình toàn bộ trò chơi AI Snake
Bao gồm: Kích thước lưới, độ phân giải màn hình, bảng màu hiện đại,
tốc độ khung hình (FPS) và các thông số thuật toán.
"""

# ==========================================
# 1. CẤU HÌNH LƯỚI BẢN ĐỒ (GRID CONFIGURATION)
# ==========================================
GRID_WIDTH = 20       # Số cột mặc định (20)
GRID_HEIGHT = 20      # Số hàng mặc định (20)
CELL_SIZE = 30        # Kích thước mỗi ô vuông (pixel)

# Kích thước khung bàn cờ
BOARD_WIDTH = GRID_WIDTH * CELL_SIZE    # 600 px
BOARD_HEIGHT = GRID_HEIGHT * CELL_SIZE  # 600 px

# Kích thước Sidebar bảng điều khiển
SIDEBAR_WIDTH = 360                     # 360 px
WINDOW_WIDTH = BOARD_WIDTH + SIDEBAR_WIDTH  # 960 px
WINDOW_HEIGHT = BOARD_HEIGHT            # 600 px

# ==========================================
# 2. CẤU HÌNH TỐC ĐỘ VÀ FPS
# ==========================================
FPS_LEVELS = {
    "Rất chậm": 5,
    "Chậm": 12,
    "Bình thường": 25,
    "Nhanh": 50,
    "Cực nhanh": 100,
    "Tối đa (Turbo)": 200
}
DEFAULT_FPS_INDEX = 2  # Mặc định là "Bình thường" (25 FPS)

# ==========================================
# 3. BẢNG MÀU HIỆN ĐẠI (COLOR PALETTE)
# ==========================================
# Màu nền chung & Bản cờ
COLOR_BG = (18, 22, 34)              # Nền cửa sổ tối sâu
COLOR_BOARD_BG = (23, 28, 43)        # Nền bàn cờ
COLOR_GRID_LINE = (34, 41, 62)       # Đường kẻ lưới mảnh

# Rắn săn mồi
COLOR_SNAKE_HEAD = (46, 204, 113)     # Xanh lục bảo sáng cho đầu rắn
COLOR_SNAKE_BODY_START = (39, 174, 96)# Xanh lá gradient
COLOR_SNAKE_BODY_END = (26, 188, 156) # Xanh ngọc lam cuối thân
COLOR_SNAKE_EYES = (255, 255, 255)    # Mắt rắn trắng
COLOR_SNAKE_PUPIL = (20, 20, 20)      # Đồng tử đen

# Thức ăn
COLOR_FOOD = (231, 76, 60)           # Đỏ tươi nổi bật
COLOR_FOOD_GLOW = (255, 107, 107)    # Vầng sáng thức ăn

# Trực quan hóa thuật toán
COLOR_ASTAR_PATH = (241, 196, 15)       # Vàng tươi cho đường đi A*
COLOR_ASTAR_SEARCH = (52, 152, 219)     # Xanh dương cho các nút Open/Closed
COLOR_HAMILTONIAN_CYCLE = (155, 89, 182)# Tím thạch anh cho chu trình Hamiltonian

# Sidebar & Giao diện Dashboard
COLOR_SIDEBAR_BG = (20, 24, 38)
COLOR_CARD_BG = (28, 34, 52)
COLOR_CARD_BORDER = (45, 54, 80)
COLOR_TEXT_MAIN = (245, 247, 250)
COLOR_TEXT_MUTED = (149, 165, 166)
COLOR_TEXT_ACCENT = (0, 210, 211)

# Nút bấm (Buttons)
COLOR_BTN_DEFAULT = (41, 128, 185)
COLOR_BTN_HOVER = (52, 152, 219)
COLOR_BTN_ACTIVE = (39, 174, 96)
COLOR_BTN_DANGER = (192, 57, 43)
COLOR_BTN_DANGER_HOVER = (231, 76, 60)
COLOR_BTN_TEXT = (255, 255, 255)

# ==========================================
# 4. CHẾ ĐỘ HOẠT ĐỘNG CỦA AI (AI MODES)
# ==========================================
AI_MODE_SMART_HYBRID = "A* + Hamiltonian (Tối ưu)"
AI_MODE_PURE_HAMILTONIAN = "Chu trình Hamiltonian thuần"
AI_MODE_PURE_ASTAR = "A* Pathfinding thuần"

AI_MODES = [
    AI_MODE_SMART_HYBRID,
    AI_MODE_PURE_HAMILTONIAN,
    AI_MODE_PURE_ASTAR
]
