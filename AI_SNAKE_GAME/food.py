"""
food.py - Quản lý thức ăn trong game
Chịu trách nhiệm tạo vị trí thức ăn ngẫu nhiên, đảm bảo không trùng
với thân rắn và phát hiện điều kiện phủ kín 100% bản đồ.
"""

import random
from typing import List, Tuple, Set, Optional


class Food:
    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.position: Optional[Tuple[int, int]] = None

    def respawn(self, snake_body: List[Tuple[int, int]]) -> bool:
        """
        Sinh thức ăn ở một vị trí trống ngẫu nhiên không thuộc thân rắn.
        Trả về True nếu sinh thành công, False nếu bản đồ đã bị rắn lấp đầy 100% (chiến thắng).
        """
        snake_set: Set[Tuple[int, int]] = set(snake_body)
        total_cells = self.grid_width * self.grid_height

        if len(snake_set) >= total_cells:
            self.position = None
            return False  # Toàn bộ bản đồ đã bị chiếm giữ!

        available_cells = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if (x, y) not in snake_set
        ]

        if not available_cells:
            self.position = None
            return False

        self.position = random.choice(available_cells)
        return True
