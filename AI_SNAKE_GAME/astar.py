import heapq
from typing import List, Tuple, Set, Dict, Optional


def manhattan_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def get_neighbors(
    pos: Tuple[int, int],
    grid_w: int,
    grid_h: int,
    obstacles: Set[Tuple[int, int]]
) -> List[Tuple[int, int]]:
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
            if start == goal:
            return [start], []
        open_heap = []
        counter = 0
        heapq.heappush(open_heap, (0, counter, start))

        closed_set: Set[Tuple[int, int]] = set()

        visited_nodes: List[Tuple[int, int]] = []

        g_score: Dict[Tuple[int, int], float] = {start: 0.0}
        f_score: Dict[Tuple[int, int], float] = {start: float(manhattan_distance(start, goal))}

        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

        open_set_hash: Set[Tuple[int, int]] = {start}

        while open_heap:
            current_f, _, current = heapq.heappop(open_heap)
            open_set_hash.discard(current)

            if current not in closed_set:
                closed_set.add(current)
                visited_nodes.append(current)

            if current == goal:
                path = []
                curr = current
                while curr in came_from:
                    path.append(curr)
                    curr = came_from[curr]
                path.append(start)
                path.reverse()
                return path, visited_nodes

            for neighbor in get_neighbors(current, self.grid_w, self.grid_h, obstacles):
                if neighbor in closed_set:
                    continue

                tentative_g = g_score[current] + 1.0

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_val = tentative_g + manhattan_distance(neighbor, goal)
                    f_score[neighbor] = f_val

                    if neighbor not in open_set_hash:
                        counter += 1
                        heapq.heappush(open_heap, (f_val, counter, neighbor))
                        open_set_hash.add(neighbor)

        return None, visited_nodes

    def is_tail_reachable(
        self,
        simulated_body: List[Tuple[int, int]]
    ) -> bool:

        if len(simulated_body) < 2:
            return True

        start = simulated_body[0]
        tail = simulated_body[-1]

        obstacles = set(simulated_body[:-1])

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
