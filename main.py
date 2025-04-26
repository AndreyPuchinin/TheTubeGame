import random
from enum import Enum


class Direction(Enum):
    UP = 'U'
    DOWN = 'D'
    LEFT = 'L'
    RIGHT = 'R'


class CorridorCell:
    def __init__(self, direction, length=50):
        self.direction = direction
        self.length = length  # Длина сегмента в пикселях
        self.connections = []  # Для хранения информации о соединениях (понадобится позже)

    def __repr__(self):
        return f"CorridorCell({self.direction.value}, length={self.length})"


class Corridor:
    def __init__(self, initial_direction=Direction.RIGHT, segment_length=50):
        self.cells = [CorridorCell(initial_direction, segment_length)]
        self.current_position = (0, 0)  # Текущая позиция конца коридора
        self.segment_length = segment_length

    def add_random_cell(self):
        # Исключаем движение "назад" чтобы избежать немедленных пересечений
        last_dir = self.cells[-1].direction
        possible_directions = [d for d in Direction if d != self._get_opposite_direction(last_dir)]

        new_direction = random.choice(possible_directions)
        new_cell = CorridorCell(new_direction, self.segment_length)
        self.cells.append(new_cell)

        # Обновляем текущую позицию
        self._update_position(new_direction)

    def _get_opposite_direction(self, direction):
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return opposites[direction]

    def _update_position(self, new_direction):
        x, y = self.current_position
        if new_direction == Direction.UP:
            self.current_position = (x, y - self.segment_length)
        elif new_direction == Direction.DOWN:
            self.current_position = (x, y + self.segment_length)
        elif new_direction == Direction.LEFT:
            self.current_position = (x - self.segment_length, y)
        elif new_direction == Direction.RIGHT:
            self.current_position = (x + self.segment_length, y)

    def generate_sequence(self, num_cells):
        for _ in range(num_cells - 1):  # -1 потому что начальная клетка уже есть
            self.add_random_cell()

    def get_direction_sequence(self):
        return ''.join(cell.direction.value for cell in self.cells)

    def get_required_cells_to_exit_screen(self, screen_width, screen_height):
        """Возвращает сколько нужно клеток, чтобы коридор вышел за пределы экрана"""
        x, y = 0, 0  # Начинаем от центра
        min_x, max_x = 0, 0
        min_y, max_y = 0, 0

        for i, cell in enumerate(self.cells):
            if cell.direction == Direction.UP:
                y -= cell.length
            elif cell.direction == Direction.DOWN:
                y += cell.length
            elif cell.direction == Direction.LEFT:
                x -= cell.length
            elif cell.direction == Direction.RIGHT:
                x += cell.length

            # Обновляем границы
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

            # Проверяем выход за пределы экрана
            if (abs(min_x) > screen_width // 2 or abs(max_x) > screen_width // 2 or
                    abs(min_y) > screen_height // 2 or abs(max_y) > screen_height // 2):
                return i + 1  # +1 потому что индексы с 0

        # Если коридор еще не вышел за пределы экрана
        remaining_x = max(screen_width // 2 - max_x, screen_width // 2 + min_x)
        remaining_y = max(screen_height // 2 - max_y, screen_height // 2 + min_y)
        remaining = max(remaining_x, remaining_y) // self.segment_length

        return len(self.cells) + remaining


# Пример использования
if __name__ == "__main__":
    # Создаем коридор с начальным направлением вправо
    corridor = Corridor(initial_direction=Direction.RIGHT)

    # Генерируем последовательность из 10 клеток
    corridor.generate_sequence(10)

    # Получаем последовательность направлений
    sequence = corridor.get_direction_sequence()
    print("Сгенерированная последовательность:", sequence)

    # Проверяем сколько нужно клеток чтобы выйти за экран 800x600
    screen_width, screen_height = 800, 600
    required = corridor.get_required_cells_to_exit_screen(screen_width, screen_height)
    print(f"Нужно {required} клеток чтобы выйти за пределы экрана {screen_width}x{screen_height}")