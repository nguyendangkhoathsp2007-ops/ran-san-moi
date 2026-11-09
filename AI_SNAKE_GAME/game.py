"""
game.py - Quản lý trạng thái trò chơi Snake AI
Xử lý vòng lặp cập nhật, thời gian, điểm số, bắt sự kiện chuột và phím tắt,
và điều phối các module: Snake, Food, AIController, Visualizer.
"""

import pygame
import time
from typing import List
import settings
from snake import Snake
from food import Food
from controller import AIController
from visualization import Visualizer, Button


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("AI Snake Game - A* Pathfinding + Hamiltonian Cycle")

        self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # Khởi tạo các thành phần thực thể
        self.food = Food(settings.GRID_WIDTH, settings.GRID_HEIGHT)
        self.ai = AIController(settings.GRID_WIDTH, settings.GRID_HEIGHT)
        total = settings.GRID_WIDTH * settings.GRID_HEIGHT
        cycle = self.ai.hamiltonian.cycle_path
        start_body = [cycle[0], cycle[total - 1], cycle[total - 2]]
        self.snake = Snake(start_pos=cycle[0], initial_length=3, initial_body=start_body)
        self.visualizer = Visualizer(self.screen)

        # Trạng thái trò chơi
        self.is_running = True
        self.is_paused = False
        self.is_game_over = False
        self.is_won = False
        self.score = 0

        # Tốc độ khung hình (FPS)
        self.fps_keys = list(settings.FPS_LEVELS.keys())
        self.fps_index = settings.DEFAULT_FPS_INDEX

        # Thời gian chạy
        self.start_ticks = time.time()
        self.accumulated_runtime = 0.0
        self.last_update_time = time.time()

        # Sinh thức ăn đầu tiên
        self.food.respawn(self.snake.body)

        # Khởi tạo các nút bấm tương tác
        self._init_buttons()

    def _init_buttons(self):
        """Tạo các nút bấm điều khiển trực quan trên Sidebar."""
        sb_x = settings.BOARD_WIDTH + 15
        btn_w = 155
        btn_h = 32
        gap_y = 40

        # Hàng 1: [Pause / Tiếp tục] & [Khởi động lại]
        y1 = 365
        self.btn_pause = Button(
            pygame.Rect(sb_x, y1, btn_w, btn_h),
            "Tạm dừng (Space)",
            self.toggle_pause,
            color=settings.COLOR_BTN_DEFAULT,
            hover_color=settings.COLOR_BTN_HOVER
        )
        self.btn_restart = Button(
            pygame.Rect(sb_x + btn_w + 10, y1, btn_w, btn_h),
            "Chơi lại (R)",
            self.restart,
            color=settings.COLOR_BTN_DANGER,
            hover_color=settings.COLOR_BTN_DANGER_HOVER
        )

        # Hàng 2: Điều chỉnh tốc độ [- Chậm] [Tên tốc độ] [+ Nhanh]
        y2 = y1 + gap_y
        self.btn_speed_down = Button(
            pygame.Rect(sb_x, y2, 45, btn_h),
            "-",
            self.decrease_speed
        )
        self.btn_speed_info = Button(
            pygame.Rect(sb_x + 50, y2, 220, btn_h),
            f"Tốc độ: {self.fps_keys[self.fps_index]}",
            self.cycle_speed,
            color=settings.COLOR_CARD_BG,
            hover_color=settings.COLOR_CARD_BORDER
        )
        self.btn_speed_up = Button(
            pygame.Rect(sb_x + 275, y2, 45, btn_h),
            "+",
            self.increase_speed
        )

        # Hàng 3: Bật/tắt đường đi A* & Nút duyệt A*
        y3 = y2 + gap_y
        self.btn_toggle_path = Button(
            pygame.Rect(sb_x, y3, btn_w, btn_h),
            "Đường đi: BẬT",
            self.toggle_path,
            is_toggle=True,
            active=True
        )
        self.btn_toggle_nodes = Button(
            pygame.Rect(sb_x + btn_w + 10, y3, btn_w, btn_h),
            "Nút A*: BẬT",
            self.toggle_search_nodes,
            is_toggle=True,
            active=True
        )

        # Hàng 4: Bật/tắt Chu trình Hamiltonian & Đổi Chế độ AI
        y4 = y3 + gap_y
        self.btn_toggle_cycle = Button(
            pygame.Rect(sb_x, y4, btn_w, btn_h),
            "Chu trình: TẮT",
            self.toggle_hamiltonian,
            is_toggle=True,
            active=False
        )
        self.btn_mode = Button(
            pygame.Rect(sb_x + btn_w + 10, y4, btn_w, btn_h),
            "Đổi Chế Độ (M)",
            self.cycle_mode
        )

        self.visualizer.set_buttons([
            self.btn_pause,
            self.btn_restart,
            self.btn_speed_down,
            self.btn_speed_info,
            self.btn_speed_up,
            self.btn_toggle_path,
            self.btn_toggle_nodes,
            self.btn_toggle_cycle,
            self.btn_mode
        ])

    def toggle_pause(self):
        """Bật/tắt tạm dừng game."""
        self.is_paused = not self.is_paused
        self.btn_pause.text = "Tiếp tục (Space)" if self.is_paused else "Tạm dừng (Space)"

    def restart(self):
        """Khởi động lại toàn bộ trò chơi về trạng thái ban đầu."""
        total = settings.GRID_WIDTH * settings.GRID_HEIGHT
        cycle = self.ai.hamiltonian.cycle_path
        start_body = [cycle[0], cycle[total - 1], cycle[total - 2]]
        self.snake.reset(initial_body=start_body)
        self.food.respawn(self.snake.body)
        self.is_game_over = False
        self.is_won = False
        self.score = 0
        self.accumulated_runtime = 0.0
        self.start_ticks = time.time()
        self.last_update_time = time.time()
        self.ai.status_description = "Đã khởi động lại"

    def increase_speed(self):
        """Tăng tốc độ game."""
        if self.fps_index < len(self.fps_keys) - 1:
            self.fps_index += 1
            self.btn_speed_info.text = f"Tốc độ: {self.fps_keys[self.fps_index]}"

    def decrease_speed(self):
        """Giảm tốc độ game."""
        if self.fps_index > 0:
            self.fps_index -= 1
            self.btn_speed_info.text = f"Tốc độ: {self.fps_keys[self.fps_index]}"

    def cycle_speed(self):
        """Chuyển vòng tròn các mức tốc độ."""
        self.fps_index = (self.fps_index + 1) % len(self.fps_keys)
        self.btn_speed_info.text = f"Tốc độ: {self.fps_keys[self.fps_index]}"

    def toggle_path(self):
        """Bật/tắt hiển thị đường đi A*."""
        self.visualizer.show_path = not self.visualizer.show_path
        self.btn_toggle_path.text = f"Đường đi: {'BẬT' if self.visualizer.show_path else 'TẮT'}"

    def toggle_search_nodes(self):
        """Bật/tắt hiển thị các nút A* đã duyệt."""
        self.visualizer.show_search_nodes = not self.visualizer.show_search_nodes
        self.btn_toggle_nodes.text = f"Nút A*: {'BẬT' if self.visualizer.show_search_nodes else 'TẮT'}"

    def toggle_hamiltonian(self):
        """Bật/tắt hiển thị chu trình Hamiltonian."""
        self.visualizer.show_hamiltonian_cycle = not self.visualizer.show_hamiltonian_cycle
        self.btn_toggle_cycle.text = f"Chu trình: {'BẬT' if self.visualizer.show_hamiltonian_cycle else 'TẮT'}"

    def cycle_mode(self):
        """Chuyển đổi giữa 3 chế độ AI."""
        current_idx = settings.AI_MODES.index(self.ai.mode)
        next_idx = (current_idx + 1) % len(settings.AI_MODES)
        self.ai.set_mode(settings.AI_MODES[next_idx])

    def handle_input(self):
        """Xử lý sự kiện bàn phím và chuột."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            # Xử lý sự kiện click chuột trên nút
            self.visualizer.handle_event(event)

            # Phím tắt tiện lợi
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.toggle_pause()
                elif event.key == pygame.K_r:
                    self.restart()
                elif event.key in (pygame.K_UP, pygame.K_RIGHT):
                    self.increase_speed()
                elif event.key in (pygame.K_DOWN, pygame.K_LEFT):
                    self.decrease_speed()
                elif event.key == pygame.K_p:
                    self.toggle_path()
                elif event.key == pygame.K_s:
                    self.toggle_search_nodes()
                elif event.key == pygame.K_h:
                    self.toggle_hamiltonian()
                elif event.key == pygame.K_m:
                    self.cycle_mode()

    def update(self):
        """Cập nhật một bước đi của rắn theo quyết định của AI."""
        now = time.time()
        if not self.is_paused and not self.is_game_over and not self.is_won:
            self.accumulated_runtime += (now - self.last_update_time)
        self.last_update_time = now

        if self.is_paused or self.is_game_over or self.is_won:
            return

        # 1. AI tính toán bước đi tiếp theo
        next_pos = self.ai.get_next_move(self.snake, self.food)

        if next_pos is None:
            self.is_game_over = True
            self.ai.status_description = "Không tìm thấy bước đi an toàn"
            return

        # 2. Kiểm tra va chạm với tường hoặc thân rắn
        will_eat = (next_pos == self.food.position)
        if self.snake.will_collide(next_pos, settings.GRID_WIDTH, settings.GRID_HEIGHT, will_grow=will_eat):
            self.is_game_over = True
            self.snake.alive = False
            self.ai.status_description = "Va chạm! Kết thúc trò chơi"
            return

        # 3. Rắn thực hiện di chuyển
        self.snake.move(next_pos, grow=will_eat)

        # 4. Nếu ăn thức ăn
        if will_eat:
            self.score += 10
            respawn_success = self.food.respawn(self.snake.body)
            if not respawn_success:
                # Toàn bộ lưới đã được lấp đầy 100%!
                self.is_won = True
                self.ai.status_description = "CHIẾN THẮNG! Phủ kín 100% bản đồ!"

    def run(self):
        """Vòng lặp chính của trò chơi (Main Game Loop)."""
        while self.is_running:
            # 1. Bắt tương tác người dùng
            self.handle_input()

            # 2. Cập nhật logic game
            self.update()

            # 3. Vẽ toàn bộ giao diện
            current_fps = settings.FPS_LEVELS[self.fps_keys[self.fps_index]]
            self.visualizer.draw_all(
                snake=self.snake,
                food=self.food,
                ai=self.ai,
                score=self.score,
                runtime_seconds=self.accumulated_runtime,
                is_paused=self.is_paused,
                is_game_over=self.is_game_over,
                is_won=self.is_won,
                current_fps_name=self.fps_keys[self.fps_index]
            )

            # 4. Hiển thị lên màn hình
            pygame.display.flip()

            # 5. Điều tiết tốc độ khung hình
            self.clock.tick(current_fps)

        pygame.quit()
