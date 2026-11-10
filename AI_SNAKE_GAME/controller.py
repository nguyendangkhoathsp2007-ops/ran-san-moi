from typing import List, Tuple, Set, Optional
from astar import AStar, get_neighbors
from hamiltonian import HamiltonianCycle
from snake import Snake
from food import Food
import settings


class AIController:
    def __init__(self, grid_w: int, grid_h: int):
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.total_cells = grid_w * grid_h

        self.astar = AStar(grid_w, grid_h)
        self.hamiltonian = HamiltonianCycle(grid_w, grid_h)

        self.mode = settings.AI_MODE_SMART_HYBRID

        self.last_path: List[Tuple[int, int]] = []
        self.last_visited_nodes: List[Tuple[int, int]] = []
        self.nodes_explored_count: int = 0
        self.current_strategy: str = "Khởi tạo"
        self.status_description: str = "Sẵn sàng"

    def set_mode(self, new_mode: str):
        if new_mode in settings.AI_MODES:
            self.mode = new_mode

    def get_next_move(self, snake: Snake, food: Food) -> Optional[Tuple[int, int]]:
   
        if not snake.alive or food.position is None:
            return None

        self.last_path = []
        self.last_visited_nodes = []
        self.nodes_explored_count = 0

        head = snake.head
        food_pos = food.position
        snake_len = snake.length
        coverage_ratio = snake_len / self.total_cells

        if self.mode == settings.AI_MODE_PURE_HAMILTONIAN:
            self.current_strategy = "Hamiltonian thuần"
            self.status_description = "Bám sát chu trình chuẩn để lấp đầy 100%"
            next_step = self.hamiltonian.get_next_step(head)
            self.last_path = [head, next_step]
            return next_step

        if self.mode == settings.AI_MODE_PURE_ASTAR:
            obstacles = set(snake.body[:-1]) 
            path, visited = self.astar.find_path(head, food_pos, obstacles)
            self.last_visited_nodes = visited
            self.nodes_explored_count = len(visited)

            if path and len(path) > 1:
                self.current_strategy = "A* Search"
                self.status_description = "Đi đường ngắn nhất tới mồi"
                self.last_path = path
                return path[1]
            else:
                return self._find_survival_move(snake)

        if coverage_ratio >= 0.70:
            return self._execute_safe_endgame_move(snake, food)

        return self._execute_hybrid_move(snake, food)

    def _execute_hybrid_move(self, snake: Snake, food: Food) -> Tuple[int, int]:
        """Chiến lược kết hợp tối ưu: Tìm đường A* và đi tắt an toàn theo chu trình."""
        head = snake.head
        tail = snake.tail
        food_pos = food.position
        obstacles = set(snake.body[:-1])

        path, visited = self.astar.find_path(head, food_pos, obstacles)
        self.last_visited_nodes = visited
        self.nodes_explored_count = len(visited)
        if path:
            self.last_path = path

        if path and len(path) > 1:
            astar_step = path[1]
            if self.hamiltonian.is_safe_step(head, astar_step, tail, food_pos, snake.body, snake.length):
                self.current_strategy = "A* Săn mồi (Đi tắt)"
                self.status_description = "A* tối ưu khoảng cách tới mồi"
                return astar_step

        best_shortcut = self._find_best_hamiltonian_shortcut(snake, food_pos)
        if best_shortcut:
            self.current_strategy = "Đi tắt Hamiltonian"
            self.status_description = "Rút ngắn chu trình Hamiltonian an toàn"
            if not path:
                self.last_path = [head, best_shortcut]
            return best_shortcut

        hamiltonian_next = self.hamiltonian.get_next_step(head)
        if not snake.will_collide(hamiltonian_next, self.grid_w, self.grid_h):
            self.current_strategy = "Chu trình Hamiltonian"
            self.status_description = "Bám sát chu trình bảo đảm lấp đầy 100%"
            if not path:
                self.last_path = [head, hamiltonian_next]
            return hamiltonian_next

        return self._find_survival_move(snake)

    def _execute_safe_endgame_move(self, snake: Snake, food: Food) -> Tuple[int, int]:
        head = snake.head
        obstacles = set(snake.body[:-1])

        path, visited = self.astar.find_path(head, food.position, obstacles)
        self.last_visited_nodes = visited
        self.nodes_explored_count = len(visited)
        if path:
            self.last_path = path

        hamiltonian_next = self.hamiltonian.get_next_step(head)
        if not snake.will_collide(hamiltonian_next, self.grid_w, self.grid_h):
            self.current_strategy = "Hamiltonian 100% Map"
            self.status_description = f"Phủ kín 100% bản đồ ({snake.length}/{self.total_cells})"
            return hamiltonian_next

        return self._find_survival_move(snake)

    def _find_best_hamiltonian_shortcut(self, snake: Snake, food_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:

        head = snake.head
        tail = snake.tail
        dist_head_food = self.hamiltonian.get_distance(head, food_pos)

        neighbors = get_neighbors(head, self.grid_w, self.grid_h, set(snake.body[:-1]))
        best_cand = None
        min_dist_to_food = dist_head_food

        for cand in neighbors:
            if not self.hamiltonian.is_safe_step(head, cand, tail, food_pos, snake.body, snake.length):
                continue

            dist_cand_food = self.hamiltonian.get_distance(cand, food_pos)
            if dist_cand_food < min_dist_to_food:
                min_dist_to_food = dist_cand_food
                best_cand = cand

        return best_cand

    def _find_survival_move(self, snake: Snake) -> Tuple[int, int]:

        head = snake.head
        obstacles = set(snake.body[:-1])
        neighbors = get_neighbors(head, self.grid_w, self.grid_h, obstacles)

        if not neighbors:
            self.current_strategy = "Mắc kẹt"
            self.status_description = "Không còn ô trống hợp lệ"
            return (head[0] + snake.direction[0], head[1] + snake.direction[1])

        best_neighbor = neighbors[0]
        max_free_cells = -1

        for nb in neighbors:
            free_cells = self._count_reachable_space(nb, obstacles)
            if free_cells > max_free_cells:
                max_free_cells = free_cells
                best_neighbor = nb

        self.current_strategy = "Sinh tồn (Flood Fill)"
        self.status_description = f"Chọn vùng rộng nhất ({max_free_cells} ô) tránh ngõ cụt"
        self.last_path = [head, best_neighbor]
        return best_neighbor

    def _count_reachable_space(self, start_pos: Tuple[int, int], obstacles: Set[Tuple[int, int]]) -> int:
        """Đếm số ô trống có thể đi tới từ start_pos bằng BFS."""
        from collections import deque
        queue = deque([start_pos])
        visited = {start_pos}

        while queue:
            curr = queue.popleft()
            for nb in get_neighbors(curr, self.grid_w, self.grid_h, obstacles):
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)

        return len(visited)
