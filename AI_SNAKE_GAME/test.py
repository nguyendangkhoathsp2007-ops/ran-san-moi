"""
test_ai.py - Bộ kiểm thử tự động toàn diện cho AI Snake Game
Kiểm tra chi tiết 6 kịch bản theo yêu cầu mục 10:
  1. Thức ăn ở vị trí gần.
  2. Thức ăn ở vị trí xa.
  3. Đường đi có nhiều vật cản phức tạp.
  4. Thức ăn xuất hiện ở vị trí mới sau khi ăn.
  5. Rắn có chiều dài lớn (Endgame / High occupancy).
  6. Xử lý tình huống ngõ cụt & sinh tồn (Dead-end survival).
  7. Tính đúng đắn toán học của Chu trình Hamiltonian 20x20.
"""

import unittest
from astar import AStar, manhattan_distance, get_neighbors
from hamiltonian import HamiltonianCycle
from snake import Snake
from food import Food
from ai_controller import AIController
import settings


class TestAISnake(unittest.TestCase):

    def setUp(self):
        self.grid_w = 20
        self.grid_h = 20
        self.total_cells = self.grid_w * self.grid_h
        self.astar = AStar(self.grid_w, self.grid_h)
        self.hamiltonian = HamiltonianCycle(self.grid_w, self.grid_h)
        self.ai = AIController(self.grid_w, self.grid_h)

    def test_01_hamiltonian_cycle_validity(self):
        """Kiểm tra tính đúng đắn toán học của chu trình Hamiltonian 20x20."""
        self.assertTrue(self.hamiltonian.is_valid, "Chu trình Hamiltonian phải hợp lệ")
        self.assertEqual(len(self.hamiltonian.cycle_path), self.total_cells, "Chu trình phải chứa đủ 400 ô")

        # Kiểm tra tập hợp các ô phủ kín 100% không trùng lặp
        all_cells = {(x, y) for x in range(self.grid_w) for y in range(self.grid_h)}
        cycle_cells = set(self.hamiltonian.cycle_path)
        self.assertEqual(all_cells, cycle_cells, "Chu trình phải đi qua toàn bộ 400 ô trên bản đồ")

        # Kiểm tra từng bước đi liên tiếp kề nhau (Manhattan distance = 1)
        path = self.hamiltonian.cycle_path
        for i in range(len(path)):
            curr = path[i]
            nxt = path[(i + 1) % len(path)]
            self.assertEqual(
                manhattan_distance(curr, nxt), 1,
                f"Bước từ {curr} tới {nxt} không kề nhau!"
            )

    def test_02_astar_near_food(self):
        """Kịch bản 1: AI tìm được thức ăn ở vị trí gần (khoảng cách 1-3 ô)."""
        start = (5, 5)
        goal = (5, 7)
        obstacles = set()
        path, visited = self.astar.find_path(start, goal, obstacles)

        self.assertIsNotNone(path, "A* phải tìm thấy đường đi tới thức ăn gần")
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
        self.assertEqual(len(path) - 1, 2, "Độ dài đường đi phải đúng khoảng cách Manhattan")
        self.assertTrue(len(visited) > 0, "Danh sách nút xét phải được ghi nhận")

    def test_03_astar_far_food(self):
        """Kịch bản 2: AI tìm được thức ăn ở vị trí xa (hai góc đối diện bản đồ)."""
        start = (0, 0)
        goal = (19, 19)
        obstacles = set()
        path, visited = self.astar.find_path(start, goal, obstacles)

        self.assertIsNotNone(path, "A* phải tìm thấy đường đi tới thức ăn xa")
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)
        expected_dist = manhattan_distance(start, goal)  # 19 + 19 = 38
        self.assertEqual(len(path) - 1, expected_dist, "Độ dài đường đi không vật cản phải bằng khoảng cách Manhattan")

    def test_04_astar_with_heavy_obstacles(self):
        """Kịch bản 3: Đường đi có nhiều vật cản (bức tường chắn ngang)."""
        start = (5, 5)
        goal = (5, 9)
        # Tạo một bức tường ngang chặn giữa y = 7 từ x=3 đến x=7
        wall = {(x, 7) for x in range(3, 8)}
        path, visited = self.astar.find_path(start, goal, wall)

        self.assertIsNotNone(path, "A* phải đi vòng qua tường thành công")
        self.assertEqual(path[-1], goal)
        # Đảm bảo không có ô nào trên đường đi trùng với tường
        for step in path:
            self.assertNotIn(step, wall, f"Đường đi A* không được xuyên qua tường: {step}")

    def test_05_food_respawn_new_positions(self):
        """Kịch bản 4: Thức ăn xuất hiện ở vị trí mới sau khi ăn."""
        food = Food(self.grid_w, self.grid_h)
        snake = Snake(start_pos=(5, 5), initial_length=5)

        # Sinh thức ăn lần 1
        success_1 = food.respawn(snake.body)
        self.assertTrue(success_1)
        pos_1 = food.position
        self.assertNotIn(pos_1, snake.body, "Thức ăn không được sinh trên thân rắn")

        # Rắn di chuyển và ăn thức ăn
        snake.move(pos_1, grow=True)
        # Sinh thức ăn lần 2
        success_2 = food.respawn(snake.body)
        self.assertTrue(success_2)
        pos_2 = food.position
        self.assertNotIn(pos_2, snake.body, "Thức ăn mới không được trùng thân rắn đã dài thêm")

    def test_06_long_snake_decision(self):
        """Kịch bản 5: Rắn có chiều dài lớn (ví dụ: chiếm 70% bản đồ = 280 ô)."""
        # Tạo thân rắn dài dọc theo chu trình Hamiltonian
        long_body = self.hamiltonian.cycle_path[:280]
        snake = Snake(start_pos=long_body[0], initial_length=len(long_body))
        snake.body = list(long_body)

        food = Food(self.grid_w, self.grid_h)
        food.respawn(snake.body)

        # AI controller phải đưa ra bước đi an toàn, không tự đâm vào thân
        next_step = self.ai.get_next_move(snake, food)
        self.assertIsNotNone(next_step, "AI phải chọn được bước đi an toàn khi rắn dài")
        self.assertFalse(
            snake.will_collide(next_step, self.grid_w, self.grid_h),
            f"Bước đi {next_step} gây va chạm khi thân rắn dài!"
        )

    def test_07_dead_end_survival_fallback(self):
        """Kịch bản 6: AI gặp tình huống ngõ cụt, chuyển sang cơ chế sinh tồn Flood Fill."""
        snake = Snake(start_pos=(1, 1), initial_length=3)
        # Đặt thân rắn bao bọc 3 hướng quanh đầu (1, 1), chỉ để hở duy nhất hướng (1, 2)
        snake.body = [(1, 1), (0, 1), (1, 0), (2, 1), (3, 1)]
        # Obstacles = thân rắn (trừ đuôi)
        # AI phải chọn hướng đi về phía ô trống mở rộng nhất
        food = Food(self.grid_w, self.grid_h)
        food.position = (15, 15)  # Mồi ở rất xa ngoài vùng bị nhốt

        next_move = self.ai.get_next_move(snake, food)
        self.assertIsNotNone(next_move)
        # Bước đi không được đâm vào các ô thân đang cản
        self.assertEqual(next_move, (1, 2), "AI phải chọn hướng mở tự do duy nhất (1, 2)")


if __name__ == "__main__":
    unittest.main()
