"""
astar.py - Cài đặt hoàn chỉnh thuật toán A* Search (Pathfinding)
Sử dụng:
  - Công thức: f(n) = g(n) + h(n)
  - Hàm Heuristic Manhattan: h(n) = |x1 - x2| + |y1 - y2|
  - Open Set (Priority Queue - Min Heap)
  - Closed Set (Visited Set)
  - G-Score và F-Score map
  - Reconstruct Path qua Parent map
  - Thu thập tập các nút đã duyệt để hiển thị trực quan hóa (visualization)
  - Kiểm tra khả năng vươn tới đuôi (Tail Reachability / Survival Check)
"""

import heapq
from typing import List, Tuple, Set, Dict, Optional


def manhattan_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    """Hàm ước lượng Heuristic Manhattan Distance."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def get_neighbors(
    pos: Tuple[int, int],
    grid_w: int,
    grid_h: int,
    obstacles: Set[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """Lấy danh sách các ô kề hợp lệ (không vượt biên và không chạm chướng ngại vật)."""
    x, y = pos
    candidates = [
        (x + 1, y),  # Phải
        (x - 1, y),  # Trái
        (x, y + 1),  # Xuống
        (x, y - 1)   # Lên
    ]
    valid_neighbors = []
    for nx, ny in candidates:
        if 0 <= nx < grid_w and 0 <= ny < grid_h and (nx, ny) not in obstacles:
            valid_neighbors.append((nx, ny))
    return valid_neighbors


class AStar:
    def __init__(self, grid_w: int, grid_h: int):
        self.grid_w = grid_w
        self.grid_h = grid_h

    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        obstacles: Set[Tuple[int, int]]
    ) -> Tuple[Optional[List[Tuple[int, int]]], List[Tuple[int, int]]]:
        """
        Tìm đường đi ngắn nhất từ start đến goal bằng thuật toán A*.

        Returns:
            - path: Danh sách các tọa độ [start, step_1, ..., goal] nếu tìm thấy đường, ngược lại None.
            - visited_nodes: Danh sách thứ tự các ô đã được lấy ra từ Open Set để xét (phục vụ trực quan hóa).
        """
        if start == goal:
            return [start], []

        # Open Set lưu dạng bộ (f_score, counter, current_node)
        # Counter giúp giải quyết xung đột khi f_score bằng nhau mà không so sánh tuple tọa độ
        open_heap = []
        counter = 0
        heapq.heappush(open_heap, (0, counter, start))

        # Closed set lưu các nút đã hoàn tất đánh giá
        closed_set: Set[Tuple[int, int]] = set()

        # Danh sách ghi nhận thứ tự duyệt nút để visualization
        visited_nodes: List[Tuple[int, int]] = []

        # Bảng ghi nhớ chi phí g(n) và f(n)
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}
        f_score: Dict[Tuple[int, int], float] = {start: float(manhattan_distance(start, goal))}

        # Bảng phụ huynh để truy vết đường đi (Parent pointer)
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

        # Set hỗ trợ kiểm tra nhanh các phần tử đang có trong Open Set
        open_set_hash: Set[Tuple[int, int]] = {start}

        while open_heap:
            current_f, _, current = heapq.heappop(open_heap)
            open_set_hash.discard(current)

            # Ghi nhận nút đã được xét
            if current not in closed_set:
                closed_set.add(current)
                visited_nodes.append(current)

            # Nếu đã đến đích -> Khôi phục đường đi từ Parent map
            if current == goal:
                path = []
                curr = current
                while curr in came_from:
                    path.append(curr)
                    curr = came_from[curr]
                path.append(start)
                path.reverse()
                return path, visited_nodes

            # Xét các nút kề
            for neighbor in get_neighbors(current, self.grid_w, self.grid_h, obstacles):
                if neighbor in closed_set:
                    continue

                tentative_g = g_score[current] + 1.0

                if tentative_g < g_score.get(neighbor, float('inf')):
                    # Tìm thấy đường tốt hơn đến neighbor
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_val = tentative_g + manhattan_distance(neighbor, goal)
                    f_score[neighbor] = f_val

                    if neighbor not in open_set_hash:
                        counter += 1
                        heapq.heappush(open_heap, (f_val, counter, neighbor))
                        open_set_hash.add(neighbor)

        # Không tìm được đường đi
        return None, visited_nodes

    def is_tail_reachable(
        self,
        simulated_body: List[Tuple[int, int]]
    ) -> bool:
        """
        Kiểm tra từ đầu mới của rắn có đường đi an toàn để tiếp cận đuôi không (Breadth-First Search).
        Đây là kỹ thuật bảo vệ tối quan trọng: nếu rắn ăn thức ăn xong mà không còn đường tới đuôi,
        nó chắc chắn sẽ tự nhốt mình vào ngõ cụt chết chóc!
        """
        if len(simulated_body) < 2:
            return True

        start = simulated_body[0]
        tail = simulated_body[-1]

        # Đuôi được coi là điểm đến hợp lệ vì khi rắn di chuyển, ô đuôi sẽ trống ra
        obstacles = set(simulated_body[:-1])

        # BFS nhanh tìm đường từ đầu tới đuôi
        from collections import deque
        queue = deque([start])
        visited = {start}

        while queue:
            current = queue.popleft()
            if current == tail:
                return True

            for nb in get_neighbors(current, self.grid_w, self.grid_h, obstacles):
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)

        return False
