import random
from enum import Enum
from typing import Tuple, List, Dict
from collections import deque


class Direction(Enum):
    UP = 'U'
    DOWN = 'D'
    LEFT = 'L'
    RIGHT = 'R'

    @classmethod
    def random(cls) -> 'Direction':
        return random.choice(list(Direction))

    def opposite(self) -> 'Direction':
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }[self]


class CorridorCell:
    def __init__(self, direction: Direction, length: int):
        self.direction = direction
        self.length = length
        self.connections: List[Direction] = []

    def __repr__(self) -> str:
        return f"CorridorCell({self.direction.value}, length={self.length})"


class Corridor:
    def __init__(self, screen_size: Tuple[int, int] = (800, 600)):
        self.screen_width, self.screen_height = screen_size
        self.cells = deque()
        self.segment_length_range = (30, 70)
        self.occupied_positions: Dict[Tuple[int, int], Direction] = {}

        # Инициализируем коридор достаточной длины
        self._initialize_corridor()

    def _initialize_corridor(self) -> None:
        """Инициализирует коридор достаточной длины для заполнения экрана"""
        # Начальное направление и длина
        initial_dir = Direction.random()
        initial_len = random.randint(*self.segment_length_range)
        self.cells.append(CorridorCell(initial_dir, initial_len))
        self._update_occupied_positions(0, 0, initial_dir, initial_len)

        # Продолжаем добавлять клетки пока коридор не заполнит экран
        while True:
            if self._is_screen_filled():
                break
            self._add_safe_cell()

    def _is_screen_filled(self) -> bool:
        """Проверяет, заполнен ли экран коридором"""
        if not self.cells:
            return False

        # Получаем границы коридора
        min_x, max_x, min_y, max_y = self._get_corridor_bounds()

        # Проверяем выход за пределы экрана
        return (abs(min_x) > self.screen_width // 2 or
                abs(max_x) > self.screen_width // 2 or
                abs(min_y) > self.screen_height // 2 or
                abs(max_y) > self.screen_height // 2)

    def _get_corridor_bounds(self) -> Tuple[int, int, int, int]:
        """Возвращает границы коридора (min_x, max_x, min_y, max_y)"""
        min_x = max_x = min_y = max_y = 0
        x, y = 0, 0

        for cell in self.cells:
            if cell.direction == Direction.UP:
                y -= cell.length
            elif cell.direction == Direction.DOWN:
                y += cell.length
            elif cell.direction == Direction.LEFT:
                x -= cell.length
            elif cell.direction == Direction.RIGHT:
                x += cell.length

            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

        return min_x, max_x, min_y, max_y

    def _update_occupied_positions(self, start_x: int, start_y: int,
                                   direction: Direction, length: int) -> None:
        """Обновляет множество занятых позиций"""
        x, y = start_x, start_y
        step_x, step_y = 0, 0

        if direction == Direction.UP:
            step_y = -1
        elif direction == Direction.DOWN:
            step_y = 1
        elif direction == Direction.LEFT:
            step_x = -1
        elif direction == Direction.RIGHT:
            step_x = 1

        for _ in range(length):
            x += step_x
            y += step_y
            self.occupied_positions[(x, y)] = direction

    def _add_safe_cell(self) -> bool:
        """Добавляет новую клетку, избегая самопересечений"""
        if not self.cells:
            return False

        last_cell = self.cells[-1]
        last_dir = last_cell.direction
        forbidden_directions = {last_dir.opposite()}

        # Получаем текущую конечную позицию
        end_x, end_y = self._get_end_position()

        # Проверяем возможные направления
        possible_dirs = [
            d for d in Direction
            if d not in forbidden_directions and
            not self._would_intersect(end_x, end_y, d)
        ]

        if not possible_dirs:
            # Невозможно добавить клетку без пересечения - удаляем последнюю и пробуем снова
            self.cells.pop()
            return self._add_safe_cell()

        # Выбираем случайное допустимое направление
        new_dir = random.choice(possible_dirs)
        new_len = random.randint(*self.segment_length_range)
        new_cell = CorridorCell(new_dir, new_len)
        self.cells.append(new_cell)

        # Обновляем занятые позиции
        self._update_occupied_positions(end_x, end_y, new_dir, new_len)
        return True

    def _would_intersect(self, start_x: int, start_y: int,
                         direction: Direction) -> bool:
        """Проверяет, будет ли новый сегмент пересекаться с существующим коридором"""
        x, y = start_x, start_y
        step_x, step_y = 0, 0
        length = random.randint(*self.segment_length_range)

        if direction == Direction.UP:
            step_y = -1
        elif direction == Direction.DOWN:
            step_y = 1
        elif direction == Direction.LEFT:
            step_x = -1
        elif direction == Direction.RIGHT:
            step_x = 1

        for _ in range(length):
            x += step_x
            y += step_y
            if (x, y) in self.occupied_positions:
                return True

        return False

    def _get_end_position(self) -> Tuple[int, int]:
        """Возвращает конечную позицию коридора"""
        x, y = 0, 0
        for cell in self.cells:
            if cell.direction == Direction.UP:
                y -= cell.length
            elif cell.direction == Direction.DOWN:
                y += cell.length
            elif cell.direction == Direction.LEFT:
                x -= cell.length
            elif cell.direction == Direction.RIGHT:
                x += cell.length
        return x, y

    def shift_corridor(self) -> None:
        """Сдвигает коридор, удаляя вышедшие за экран клетки и добавляя новые"""
        # Сдвигает на ОДНУ?.. Куда делся параметр?..
        # Удаляем клетки с начала, если они полностью вышли за экран
        while len(self.cells) > 1:
            first_cell = self.cells[0]
            bounds = self._get_corridor_bounds()

            # Проверяем, вышел ли первый сегмент полностью за экран
            if ((first_cell.direction in (Direction.LEFT, Direction.RIGHT) and
                 (bounds[1] < -self.screen_width // 2 or bounds[0] > self.screen_width // 2))):
                self.cells.popleft()
            elif ((first_cell.direction in (Direction.UP, Direction.DOWN)) and
                  (bounds[3] < -self.screen_height // 2 or bounds[2] > self.screen_height // 2)):
                self.cells.popleft()
            else:
                break

        # Добавляем новые клетки с конца
        while not self._is_screen_filled():
            self._add_safe_cell()

    def get_direction_sequence(self) -> str:
        return ''.join(cell.direction.value for cell in self.cells)

    def get_turn_points(self) -> List[Tuple[int, Direction, Direction]]:
        turns = []
        for i in range(1, len(self.cells)):
            prev_dir = self.cells[i - 1].direction
            curr_dir = self.cells[i].direction
            if prev_dir != curr_dir:
                turns.append((i, prev_dir, curr_dir))
        return turns


corridor = Corridor(screen_size=(800, 600))
print("Начальная последовательность:", corridor.get_direction_sequence())

# Сдвигаем коридор (имитация движения игрока)
corridor.shift_corridor()
print("После сдвига:", corridor.get_direction_sequence())
