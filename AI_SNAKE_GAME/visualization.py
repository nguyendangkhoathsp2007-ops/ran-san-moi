"""
visualization.py - Giao diện đồ họa, bảng điều khiển Dashboard và trực quan hóa thuật toán
Hỗ trợ:
  - Vẽ bản đồ lưới 20x20, rắn chuyển động mượt, thức ăn và hiệu ứng
  - Trực quan hóa các ô A* đã duyệt (xanh dương)
  - Trực quan hóa đường đi A* (vàng)
  - Trực quan hóa Chu trình Hamiltonian (tím)
  - Bảng Dashboard hiển thị 8 thông số thống kê thời gian thực
  - Hệ thống nút bấm tương tác (Start/Pause, Restart, Speed, Toggles, Modes)
"""

import pygame
import time
from typing import List, Tuple, Dict, Optional, Callable
import settings


class Button:
    """Nút bấm tương tác trên giao diện Pygame với hiệu ứng hover và toggle."""
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Callable[[], None],
        color: Tuple[int, int, int] = settings.COLOR_BTN_DEFAULT,
        hover_color: Tuple[int, int, int] = settings.COLOR_BTN_HOVER,
        is_toggle: bool = False,
        active: bool = False
    ):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.is_toggle = is_toggle
        self.active = active
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.is_toggle:
                    self.active = not self.active
                self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        # Chọn màu nền tùy trạng thái
        if self.is_toggle and self.active:
            bg_col = settings.COLOR_BTN_ACTIVE
        elif self.is_hovered:
            bg_col = self.hover_color
        else:
            bg_col = self.color

        # Vẽ hình chữ nhật bo góc nhẹ
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=6)
        pygame.draw.rect(surface, settings.COLOR_CARD_BORDER, self.rect, width=1, border_radius=6)

        # Vẽ text ở giữa nút
        text_surf = font.render(self.text, True, settings.COLOR_BTN_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class Visualizer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.grid_w = settings.GRID_WIDTH
        self.grid_h = settings.GRID_HEIGHT
        self.cell_size = settings.CELL_SIZE

        # Khởi tạo font chữ hệ thống
        pygame.font.init()
        # Tìm kiếm font chữ hỗ trợ Unicode tiếng Việt tốt
        font_names = ["Segoe UI", "Arial", "Calibri", "DejaVu Sans", "Helvetica"]
        self.font_title = pygame.font.SysFont(font_names, 22, bold=True)
        self.font_bold = pygame.font.SysFont(font_names, 14, bold=True)
        self.font_regular = pygame.font.SysFont(font_names, 13)
        self.font_small = pygame.font.SysFont(font_names, 11)
        self.font_btn = pygame.font.SysFont(font_names, 12, bold=True)
        self.font_big = pygame.font.SysFont(font_names, 36, bold=True)

        # Cấu hình hiển thị trực quan (Toggles)
        self.show_path: bool = True
        self.show_search_nodes: bool = True
        self.show_hamiltonian_cycle: bool = False

        # Bề mặt bán trong suốt (Transparent overlay surface)
        self.overlay_surface = pygame.Surface(
            (settings.BOARD_WIDTH, settings.BOARD_HEIGHT), pygame.SRCALPHA
        )

        # Danh sách các nút tương tác trên Sidebar
        self.buttons: List[Button] = []

    def set_buttons(self, buttons: List[Button]):
        """Gán danh sách các nút điều khiển từ Game controller."""
        self.buttons = buttons

    def handle_event(self, event: pygame.event.Event):
        """Chuyển tiếp sự kiện chuột cho các nút bấm."""
        for btn in self.buttons:
            btn.handle_event(event)

    def draw_all(
        self,
        snake,
        food,
        ai,
        score: int,
        runtime_seconds: float,
        is_paused: bool,
        is_game_over: bool,
        is_won: bool,
        current_fps_name: str
    ):
        """Vẽ toàn bộ khung cảnh: Bản cờ, rắn, mồi, trực quan hóa và Sidebar."""
        self.screen.fill(settings.COLOR_BG)

        # 1. Vẽ khu vực bàn cờ (Board Area)
        self._draw_board()

        # 2. Xóa bề mặt bán trong suốt cho lượt vẽ mới
        self.overlay_surface.fill((0, 0, 0, 0))

        # 3. Vẽ trực quan hóa thuật toán
        if self.show_hamiltonian_cycle and ai.hamiltonian.is_valid:
            self._draw_hamiltonian_cycle(ai.hamiltonian.cycle_path)

        if self.show_search_nodes and ai.last_visited_nodes:
            self._draw_search_nodes(ai.last_visited_nodes)

        if self.show_path and ai.last_path:
            self._draw_path(ai.last_path)

        # Áp bề mặt trực quan lên bàn cờ
        self.screen.blit(self.overlay_surface, (0, 0))

        # 4. Vẽ thức ăn & rắn săn mồi
        if food.position:
            self._draw_food(food.position)
        self._draw_snake(snake)

        # 5. Vẽ màn hình kết thúc / chiến thắng (nếu có)
        if is_game_over:
            self._draw_end_overlay("GAME OVER", (231, 76, 60), "Nhấn RESTART để thử lại")
        elif is_won:
            self._draw_end_overlay("CHIẾN THẮNG 100%!", (46, 204, 113), "Rắn đã phủ kín toàn bộ bản đồ!")

        # 6. Vẽ bảng thông số Dashboard bên phải (Sidebar)
        self._draw_sidebar(
            snake=snake,
            food=food,
            ai=ai,
            score=score,
            runtime_sec=runtime_seconds,
            is_paused=is_paused,
            fps_name=current_fps_name
        )

    def _draw_board(self):
        """Vẽ nền và các đường lưới mảnh của bản cờ."""
        board_rect = pygame.Rect(0, 0, settings.BOARD_WIDTH, settings.BOARD_HEIGHT)
        pygame.draw.rect(self.screen, settings.COLOR_BOARD_BG, board_rect)

        # Đường kẻ dọc
        for x in range(0, settings.BOARD_WIDTH + 1, self.cell_size):
            pygame.draw.line(self.screen, settings.COLOR_GRID_LINE, (x, 0), (x, settings.BOARD_HEIGHT), 1)

        # Đường kẻ ngang
        for y in range(0, settings.BOARD_HEIGHT + 1, self.cell_size):
            pygame.draw.line(self.screen, settings.COLOR_GRID_LINE, (0, y), (settings.BOARD_WIDTH, y), 1)

    def _draw_search_nodes(self, visited_nodes: List[Tuple[int, int]]):
        """Vẽ các ô đã được A* duyệt qua bằng màu xanh dương bán trong suốt."""
        color = (*settings.COLOR_ASTAR_SEARCH, 75)
        for gx, gy in visited_nodes:
            rx = gx * self.cell_size + 2
            ry = gy * self.cell_size + 2
            rw = self.cell_size - 4
            rh = self.cell_size - 4
            pygame.draw.rect(self.overlay_surface, color, (rx, ry, rw, rh), border_radius=4)

    def _draw_path(self, path: List[Tuple[int, int]]):
        """Vẽ đường đi A* bằng đường nối màu vàng dạ quang nổi bật."""
        if len(path) < 2:
            return

        points = []
        for gx, gy in path:
            px = gx * self.cell_size + self.cell_size // 2
            py = gy * self.cell_size + self.cell_size // 2
            points.append((px, py))

        # Vẽ đường nối vàng
        pygame.draw.lines(self.overlay_surface, settings.COLOR_ASTAR_PATH, False, points, 4)

        # Vẽ các chấm tròn nhỏ tại mỗi nút trên đường đi
        for px, py in points:
            pygame.draw.circle(self.overlay_surface, settings.COLOR_ASTAR_PATH, (px, py), 4)

    def _draw_hamiltonian_cycle(self, cycle_path: List[Tuple[int, int]]):
        """Vẽ chu trình Hamiltonian bằng các đường nét tím tinh tế."""
        if len(cycle_path) < 2:
            return

        points = [
            (gx * self.cell_size + self.cell_size // 2, gy * self.cell_size + self.cell_size // 2)
            for gx, gy in cycle_path
        ]
        # Khép kín chu trình
        points.append(points[0])

        color = (*settings.COLOR_HAMILTONIAN_CYCLE, 90)
        pygame.draw.lines(self.overlay_surface, color, False, points, 2)

    def _draw_food(self, pos: Tuple[int, int]):
        """Vẽ thức ăn màu đỏ kèm quầng sáng nhẹ."""
        cx = pos[0] * self.cell_size + self.cell_size // 2
        cy = pos[1] * self.cell_size + self.cell_size // 2
        radius = (self.cell_size // 2) - 3

        # Quầng sáng ngoài
        pygame.draw.circle(self.screen, settings.COLOR_FOOD_GLOW, (cx, cy), radius + 2, width=2)
        # Thân mồi
        pygame.draw.circle(self.screen, settings.COLOR_FOOD, (cx, cy), radius)
        # Đốm sáng tạo độ bóng
        pygame.draw.circle(self.screen, (255, 200, 200), (cx - 2, cy - 2), 2)

    def _draw_snake(self, snake):
        """Vẽ thân rắn dạng gradient xanh lá và đầu rắn kèm mắt linh hoạt."""
        if not snake.body:
            return

        body_len = len(snake.body)

        # Vẽ các đoạn thân từ đuôi lên cổ
        for i in range(body_len - 1, 0, -1):
            gx, gy = snake.body[i]
            rx = gx * self.cell_size + 2
            ry = gy * self.cell_size + 2
            rw = self.cell_size - 4
            rh = self.cell_size - 4

            # Tính toán màu gradient từ xanh lục sang xanh ngọc
            ratio = i / max(1, body_len)
            r = int(settings.COLOR_SNAKE_BODY_START[0] * (1 - ratio) + settings.COLOR_SNAKE_BODY_END[0] * ratio)
            g = int(settings.COLOR_SNAKE_BODY_START[1] * (1 - ratio) + settings.COLOR_SNAKE_BODY_END[1] * ratio)
            b = int(settings.COLOR_SNAKE_BODY_START[2] * (1 - ratio) + settings.COLOR_SNAKE_BODY_END[2] * ratio)

            pygame.draw.rect(self.screen, (r, g, b), (rx, ry, rw, rh), border_radius=6)

        # Vẽ đầu rắn
        hx, hy = snake.head
        head_rx = hx * self.cell_size + 2
        head_ry = hy * self.cell_size + 2
        head_w = self.cell_size - 4
        head_h = self.cell_size - 4
        pygame.draw.rect(self.screen, settings.COLOR_SNAKE_HEAD, (head_rx, head_ry, head_w, head_h), border_radius=8)

        # Vẽ mắt rắn hướng theo chiều di chuyển
        dx, dy = snake.direction
        cx = head_rx + head_w // 2
        cy = head_ry + head_h // 2
        eye_offset = 5
        pupil_offset = 2

        if dx == 1:  # Hướng phải
            e1 = (cx + eye_offset, cy - eye_offset)
            e2 = (cx + eye_offset, cy + eye_offset)
        elif dx == -1:  # Hướng trái
            e1 = (cx - eye_offset, cy - eye_offset)
            e2 = (cx - eye_offset, cy + eye_offset)
        elif dy == 1:  # Hướng xuống
            e1 = (cx - eye_offset, cy + eye_offset)
            e2 = (cx + eye_offset, cy + eye_offset)
        else:  # Hướng lên
            e1 = (cx - eye_offset, cy - eye_offset)
            e2 = (cx + eye_offset, cy - eye_offset)

        for ex, ey in [e1, e2]:
            pygame.draw.circle(self.screen, settings.COLOR_SNAKE_EYES, (ex, ey), 3)
            pygame.draw.circle(self.screen, settings.COLOR_SNAKE_PUPIL, (ex + dx * pupil_offset, ey + dy * pupil_offset), 1)

    def _draw_sidebar(
        self,
        snake,
        food,
        ai,
        score: int,
        runtime_sec: float,
        is_paused: bool,
        fps_name: str
    ):
        """Vẽ bảng Dashboard chi tiết bên tay phải."""
        sb_x = settings.BOARD_WIDTH
        sb_w = settings.SIDEBAR_WIDTH
        sb_h = settings.WINDOW_HEIGHT

        # Nền Sidebar
        sidebar_rect = pygame.Rect(sb_x, 0, sb_w, sb_h)
        pygame.draw.rect(self.screen, settings.COLOR_SIDEBAR_BG, sidebar_rect)
        pygame.draw.line(self.screen, settings.COLOR_CARD_BORDER, (sb_x, 0), (sb_x, sb_h), 2)

        # 1. Header Title
        title_surf = self.font_title.render("AI SNAKE GAME", True, settings.COLOR_TEXT_ACCENT)
        self.screen.blit(title_surf, (sb_x + 18, 14))

        sub_surf = self.font_small.render("A* PATHFINDING + HAMILTONIAN CYCLE", True, settings.COLOR_TEXT_MUTED)
        self.screen.blit(sub_surf, (sb_x + 18, 40))

        # 2. Khung thẻ hiển thị 8 THÔNG SỐ (METRICS)
        card_rect = pygame.Rect(sb_x + 15, 65, sb_w - 30, 290)
        pygame.draw.rect(self.screen, settings.COLOR_CARD_BG, card_rect, border_radius=8)
        pygame.draw.rect(self.screen, settings.COLOR_CARD_BORDER, card_rect, width=1, border_radius=8)

        # Tính toán các thông số
        total_cells = settings.GRID_WIDTH * settings.GRID_HEIGHT
        coverage = (snake.length / total_cells) * 100.0
        minutes = int(runtime_sec // 60)
        seconds = int(runtime_sec % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        path_len = max(0, len(ai.last_path) - 1)

        # Danh sách 8 thông số theo yêu cầu mục 8 của đề bài:
        metrics = [
            ("1. Score (Điểm):", str(score), settings.COLOR_TEXT_MAIN),
            ("2. Snake Length (Độ dài):", f"{snake.length} / {total_cells}", settings.COLOR_TEXT_MAIN),
            ("3. A* Nodes (Nút đã xét):", str(ai.nodes_explored_count), settings.COLOR_ASTAR_SEARCH),
            ("4. Path Length (Độ dài đường):", str(path_len), settings.COLOR_ASTAR_PATH),
            ("5. Map Coverage (Bao phủ):", f"{coverage:.1f}%", settings.COLOR_TEXT_ACCENT),
            ("6. AI Status (Trạng thái):", "TẠM DỪNG" if is_paused else ai.status_description[:24], (241, 196, 15) if is_paused else settings.COLOR_TEXT_MAIN),
            ("7. Algorithm (Thuật toán):", ai.current_strategy, settings.COLOR_SNAKE_HEAD),
            ("8. Runtime (Thời gian chạy):", time_str, settings.COLOR_TEXT_MAIN),
        ]

        curr_y = 75
        for label, val, val_col in metrics:
            lbl_surf = self.font_regular.render(label, True, settings.COLOR_TEXT_MUTED)
            val_surf = self.font_bold.render(val, True, val_col)
            self.screen.blit(lbl_surf, (sb_x + 25, curr_y))
            self.screen.blit(val_surf, (sb_x + 195, curr_y))
            curr_y += 24

        # Thanh tiến độ bao phủ bản đồ (Progress bar)
        bar_bg_rect = pygame.Rect(sb_x + 25, 275, sb_w - 50, 10)
        pygame.draw.rect(self.screen, (40, 48, 70), bar_bg_rect, border_radius=5)
        bar_fill_w = int((bar_bg_rect.width) * (coverage / 100.0))
        if bar_fill_w > 0:
            bar_fill_rect = pygame.Rect(sb_x + 25, 275, bar_fill_w, 10)
            pygame.draw.rect(self.screen, settings.COLOR_SNAKE_HEAD, bar_fill_rect, border_radius=5)

        # Chế độ AI hiện tại
        mode_label = self.font_small.render(f"Chế độ hiện tại: {ai.mode}", True, settings.COLOR_TEXT_ACCENT)
        self.screen.blit(mode_label, (sb_x + 25, 325))

        # 3. Vẽ các nút điều khiển (Control Buttons)
        for btn in self.buttons:
            btn.draw(self.screen, self.font_btn)

    def _draw_end_overlay(self, title: str, title_color: Tuple[int, int, int], subtitle: str):
        """Vẽ thông báo đè khi trò chơi kết thúc hoặc hoàn thành 100%."""
        overlay = pygame.Surface((settings.BOARD_WIDTH, settings.BOARD_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        t_surf = self.font_big.render(title, True, title_color)
        t_rect = t_surf.get_rect(center=(settings.BOARD_WIDTH // 2, settings.BOARD_HEIGHT // 2 - 30))
        self.screen.blit(t_surf, t_rect)

        s_surf = self.font_regular.render(subtitle, True, settings.COLOR_TEXT_MAIN)
        s_rect = s_surf.get_rect(center=(settings.BOARD_WIDTH // 2, settings.BOARD_HEIGHT // 2 + 15))
        self.screen.blit(s_surf, s_rect)
