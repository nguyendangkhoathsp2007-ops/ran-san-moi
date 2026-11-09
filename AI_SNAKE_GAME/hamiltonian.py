"""
hamiltonian.py - Tạo chu trình Hamiltonian và kiểm tra bước đi tắt (Shortcutting)
Đảm bảo tính an toàn toán học: Rắn không bao giờ tự va chạm, lấp đầy 100% bản đồ.
"""

from typing import List, Tuple, Dict, Optional, Set


class HamiltonianCycle:
    def __init__(self, grid_w: int, grid_h: int):
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.total_cells = grid_w * grid_h

        # Danh sách chu trình theo thứ tự liên tiếp
        self.cycle_path: List[Tuple[int, int]] = []
        # Tra cứu vị trí (index) của từng ô trong chu trình: (x, y) -> 0..total-1
        self.cycle_index: Dict[Tuple[int, int], int] = {}
        # Tra cứu ô kế tiếp dọc theo chu trình
        self.cycle_next: Dict[Tuple[int, int], Tuple[int, int]] = {}

        self.is_valid = self._build_cycle()

    def _build_cycle(self) -> bool:
        """
        Xây dựng chu trình Hamiltonian hoàn chỉnh cho lưới W x H.
        Áp dụng thuật toán Boustrophedon Serpentine được chứng minh toán học:
        Yêu cầu ít nhất một kích thước là số chẵn (mặc định 20x20 chẵn).
        """
        if (self.grid_w * self.grid_h) % 2 != 0:
            # Lưới có tổng số ô lẻ không tồn tại chu trình Hamiltonian dạng lưới 4 hướng
            return False

        path = []

        # 1. Hàng 0: Đi từ trái sang phải từ (0, 0) đến (grid_w - 1, 0)
        for x in range(self.grid_w):
            path.append((x, 0))

        # 2. Cột ngoài cùng bên phải (x = grid_w - 1): Đi từ hàng 1 xuống hàng grid_h - 1
        for y in range(1, self.grid_h):
            path.append((self.grid_w - 1, y))

        # 3. Các cột còn lại từ (grid_w - 2) lùi về 0:
        # Số cột còn lại là (grid_w - 1), là số lẻ nếu grid_w chẵn (ví dụ 19 cột khi grid_w=20).
        # Đi ziczac lên - xuống xen kẽ từ hàng grid_h - 1 đến hàng 1.
        col_offset = 0
        for x in range(self.grid_w - 2, -1, -1):
            if col_offset % 2 == 0:
                # Đi lên: từ grid_h - 1 về 1
                for y in range(self.grid_h - 1, 0, -1):
                    path.append((x, y))
            else:
                # Đi xuống: từ 1 đến grid_h - 1
                for y in range(1, self.grid_h):
                    path.append((x, y))
            col_offset += 1

        # Cột x = 0 sẽ kết thúc tại (0, 1).
        # Bước tiếp theo chính là (0, 0) - vị trí xuất phát, khép kín chu trình!
        if len(path) != self.total_cells:
            return False

        self.cycle_path = path

        # Khởi tạo bảng tra cứu chỉ số và ô kế tiếp
        for i, pos in enumerate(path):
            self.cycle_index[pos] = i
            next_pos = path[(i + 1) % self.total_cells]
            self.cycle_next[pos] = next_pos

        return True

    def get_distance(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> int:
        """
        Khoảng cách tính theo số bước tiến dọc chu trình một chiều từ from_pos đến to_pos.
        """
        idx_from = self.cycle_index[from_pos]
        idx_to = self.cycle_index[to_pos]
        return (idx_to - idx_from) % self.total_cells

    def get_next_step(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Lấy bước đi chuẩn tiếp theo dọc theo chu trình."""
        return self.cycle_next[pos]

    def is_safe_step(
        self,
        head: Tuple[int, int],
        cand: Tuple[int, int],
        tail: Tuple[int, int],
        food: Tuple[int, int],
        snake_body: List[Tuple[int, int]],
        snake_len: int
    ) -> bool:
        """
        Kiểm tra bước đi tắt (shortcut) có tuyệt đối an toàn và đảm bảo lấp đầy 100% bản đồ:
        1. cand không được nằm trong thân rắn.
        2. Nếu rắn đã chiếm >= 70% bản đồ, không đi tắt nữa mà bám sát chu trình chuẩn để thắng 100%.
        3. Nếu thức ăn nằm trước đuôi (d_food < d_tail):
           - Không nhảy vượt qua thức ăn (d_cand <= d_food).
           - Giữ khoảng đệm an toàn tới đuôi (d_tail - d_cand >= 2).
        4. Nếu thức ăn nằm sau đuôi (d_food >= d_tail):
           - Chỉ đi tắt nếu khoảng trống tới đuôi rộng (d_tail > 5) và sau khi nhảy còn dư đệm >= 4.
        """
        if cand in snake_body:
            return False

        if snake_len >= int(self.total_cells * 0.70):
            return False

        d_tail = self.get_distance(head, tail)
        d_cand = self.get_distance(head, cand)
        d_food = self.get_distance(head, food)

        if d_food < d_tail:
            return (d_cand <= d_food) and ((d_tail - d_cand) >= 2)
        else:
            return (d_tail > 5) and (d_cand < d_tail) and ((d_tail - d_cand) >= 4)

    def is_shortcut_safe(
        self,
        head: Tuple[int, int],
        candidate: Tuple[int, int],
        tail: Tuple[int, int],
        snake_body: List[Tuple[int, int]],
        food_pos: Optional[Tuple[int, int]] = None
    ) -> bool:
        """Hàm tương thích cho bộ kiểm thử và các module gọi ngoài."""
        if food_pos is None:
            return candidate not in snake_body and self.get_distance(head, candidate) < self.get_distance(head, tail)
        return self.is_safe_step(head, candidate, tail, food_pos, snake_body, len(snake_body))
