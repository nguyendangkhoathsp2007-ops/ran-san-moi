"""
snake.py - Xử lý chuyển động, trạng thái và kiểm tra va chạm của rắn
Bao gồm: Lưu trữ thân rắn, di chuyển, mô phỏng bước đi, kiểm tra an toàn va chạm.
"""

from typing import List, Tuple, Optional


class Snake:
    def __init__(
        self,
        start_pos: Tuple[int, int],
        initial_length: int = 3,
        initial_body: Optional[List[Tuple[int, int]]] = None
    ):
        self.initial_pos = start_pos
        self.initial_length = initial_length
        self.initial_body = initial_body
        self.body: List[Tuple[int, int]] = []
        self.direction: Tuple[int, int] = (1, 0)
        self.alive = True
        self.reset()

    def reset(self, initial_body: Optional[List[Tuple[int, int]]] = None):
        """Khởi tạo lại trạng thái rắn."""
        if initial_body:
            self.initial_body = initial_body

        if self.initial_body:
            self.body = list(self.initial_body)
            if len(self.body) >= 2:
                self.direction = (self.body[0][0] - self.body[1][0], self.body[0][1] - self.body[1][1])
            else:
                self.direction = (1, 0)
        else:
            x, y = self.initial_pos
            self.body = [(x - i, y) for i in range(self.initial_length)]
            self.direction = (1, 0)

        self.alive = True

    @property
    def head(self) -> Tuple[int, int]:
        """Tọa độ đầu rắn."""
        return self.body[0]

    @property
    def tail(self) -> Tuple[int, int]:
        """Tọa độ đuôi rắn."""
        return self.body[-1]

    @property
    def length(self) -> int:
        """Chiều dài hiện tại của rắn."""
        return len(self.body)

    def is_valid_position(self, pos: Tuple[int, int], grid_w: int, grid_h: int) -> bool:
        """Kiểm tra một tọa độ có nằm trong ranh giới bản đồ không."""
        x, y = pos
        return 0 <= x < grid_w and 0 <= y < grid_h

    def will_collide(self, next_pos: Tuple[int, int], grid_w: int, grid_h: int, will_grow: bool = False) -> bool:
        """
        Kiểm tra bước di chuyển tiếp theo có gây va chạm với tường hoặc thân rắn không.
        Lưu ý: Nếu không ăn thức ăn (will_grow=False), đuôi rắn sẽ co lại và ô đuôi trở thành hợp lệ!
        """
        x, y = next_pos
        # Va chạm với tường biên
        if not (0 <= x < grid_w and 0 <= y < grid_h):
            return True

        # Va chạm với thân rắn
        # Nếu không lớn lên, vị trí đuôi cũ sẽ được giải phóng trong lượt này
        obstacles = set(self.body) if will_grow else set(self.body[:-1])
        return next_pos in obstacles

    def move(self, next_pos: Tuple[int, int], grow: bool = False):
        """
        Thực hiện di chuyển đầu rắn sang ô next_pos.
        Nếu grow=True, không rút đuôi (rắn dài thêm 1 ô).
        """
        # Cập nhật hướng di chuyển
        self.direction = (next_pos[0] - self.head[0], next_pos[1] - self.head[1])
        # Đưa đầu mới vào vị trí đầu tiên
        self.body.insert(0, next_pos)
        # Rút đuôi nếu không ăn thức ăn
        if not grow:
            self.body.pop()

    def simulate_step(self, next_pos: Tuple[int, int], will_grow: bool = False) -> List[Tuple[int, int]]:
        """
        Mô phỏng trạng thái thân rắn sau khi di chuyển đến next_pos mà không làm thay đổi trạng thái thật.
        Hỗ trợ AI dự đoán trước cấu trúc thân rắn để tránh tự mắc kẹt.
        """
        new_body = [next_pos] + list(self.body)
        if not will_grow:
            new_body.pop()
        return new_body
