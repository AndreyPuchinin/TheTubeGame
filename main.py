import random
from enum import Enum
from typing import Tuple, List


class Direction(Enum):
    UP = 'U'
    DOWN = 'D'
    LEFT = 'L'
    RIGHT = 'R'

    @classmethod
    def random(cls) -> 'Direction':
        return random.choice(list(Direction))


class CorridorCell:
    def __init__(self, direction: Direction, length: int):
        self.direction = direction
        self.length = length
        self.connections: List[Direction] = []

    def __repr__(self) -> str:
        return f"CorridorCell({self.direction.value}, length={self.length})"


class Corridor:
    def __init__(self):
        # Рандомизация начальных параметров
        initial_dir = Direction.random()
        segment_len = random.randint(30, 70)
        self.cells = [CorridorCell(initial_dir, segment_len)]
        self.segment_length_range = (30, 70)  # Диапазон длин сегментов

    def _get_opposite_direction(self, direction: Direction) -> Direction:
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return opposites[direction]

    def add_random_cell(self) -> None:
        last_dir = self.cells[-1].direction
        possible_dirs = [d for d in Direction if d != self._get_opposite_direction(last_dir)]

        new_dir = random.choice(possible_dirs)
        new_length = random.randint(*self.segment_length_range)
        new_cell = CorridorCell(new_dir, new_length)
        self.cells.append(new_cell)

    def generate_until_exit_screen(self, screen_width: int, screen_height: int) -> None:
        """Генерирует коридор пока он не выйдет за пределы экрана"""
        while True:
            if self.get_required_cells_to_exit_screen(screen_width, screen_height) <= len(self.cells):
                break
            self.add_random_cell()

    def get_direction_sequence(self) -> str:
        return ''.join(cell.direction.value for cell in self.cells)

    def _calculate_position_after_cells(self, num_cells: int) -> Tuple[int, int]:
        """Вычисляет позицию после прохождения num_cells клеток"""
        x, y = 0, 0
        for cell in self.cells[:num_cells]:
            if cell.direction == Direction.UP:
                y -= cell.length
            elif cell.direction == Direction.DOWN:
                y += cell.length
            elif cell.direction == Direction.LEFT:
                x -= cell.length
            elif cell.direction == Direction.RIGHT:
                x += cell.length
        return x, y

    def get_required_cells_to_exit_screen(self, screen_width: int, screen_height: int) -> int:
        """Возвращает сколько нужно клеток, чтобы коридор вышел за пределы экрана"""
        half_w, half_h = screen_width // 2, screen_height // 2

        for i in range(1, len(self.cells) + 1):
            x, y = self._calculate_position_after_cells(i)

            if abs(x) > half_w or abs(y) > half_h:
                return i

        # Если текущих клеток недостаточно, оцениваем оставшееся расстояние
        last_x, last_y = self._calculate_position_after_cells(len(self.cells))
        remaining_x = max(abs(last_x) - half_w, 0)
        remaining_y = max(abs(last_y) - half_h, 0)

        if remaining_x == 0 and remaining_y == 0:
            # Коридор пока полностью на экране, оцениваем в какую сторону он идет
            if not self.cells:
                return 1

            last_dir = self.cells[-1].direction
            if last_dir in (Direction.LEFT, Direction.RIGHT):
                remaining = (half_w - abs(last_x)) // self.cells[-1].length + 1
            else:
                remaining = (half_h - abs(last_y)) // self.cells[-1].length + 1

            return len(self.cells) + remaining

        # Оцениваем сколько нужно клеток чтобы выйти за экран
        if remaining_x > 0:
            cells_needed = remaining_x // self.cells[-1].length + 1
        else:
            cells_needed = remaining_y // self.cells[-1].length + 1

        return len(self.cells) + cells_needed

    def get_turn_points(self) -> List[Tuple[int, Direction, Direction]]:
        """Возвращает точки поворотов: (индекс клетки, откуда, куда)"""
        turns = []
        for i in range(1, len(self.cells)):
            prev_dir = self.cells[i - 1].direction
            curr_dir = self.cells[i].direction
            if prev_dir != curr_dir:
                turns.append((i, prev_dir, curr_dir))
        return turns


# Пример использования
if __name__ == "__main__":
    corridor = Corridor()
    screen_size = (800, 600)

    print("Начальное направление:", corridor.get_direction_sequence())
    corridor.generate_until_exit_screen(*screen_size)

    print("Полная последовательность:", corridor.get_direction_sequence())
    print("Количество клеток:", len(corridor.cells))
    print("Точки поворотов:")
    for turn in corridor.get_turn_points():
        print(f"Клетка {turn[0]}: {turn[1].value} -> {turn[2].value}")