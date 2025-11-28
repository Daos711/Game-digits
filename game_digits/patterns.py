"""
Module for generating tile appearance patterns.
All patterns return a list of (row, col) tuples in the order tiles should appear.
"""
import random
from game_digits.constants import BOARD_SIZE


def snake_by_rows(reverse_start=False):
    """Snake pattern by rows (left-right, then right-left, etc.)."""
    positions = []
    for row in range(BOARD_SIZE):
        cols = range(BOARD_SIZE) if (row % 2 == 0) != reverse_start else range(BOARD_SIZE - 1, -1, -1)
        for col in cols:
            positions.append((row, col))
    return positions


def snake_by_rows_reverse():
    """Snake pattern by rows, starting from bottom."""
    positions = []
    for row in range(BOARD_SIZE - 1, -1, -1):
        cols = range(BOARD_SIZE) if ((BOARD_SIZE - 1 - row) % 2 == 0) else range(BOARD_SIZE - 1, -1, -1)
        for col in cols:
            positions.append((row, col))
    return positions


def snake_by_cols(reverse_start=False):
    """Snake pattern by columns (top-down, then down-top, etc.)."""
    positions = []
    for col in range(BOARD_SIZE):
        rows = range(BOARD_SIZE) if (col % 2 == 0) != reverse_start else range(BOARD_SIZE - 1, -1, -1)
        for row in rows:
            positions.append((row, col))
    return positions


def snake_by_cols_reverse():
    """Snake pattern by columns, starting from right."""
    positions = []
    for col in range(BOARD_SIZE - 1, -1, -1):
        rows = range(BOARD_SIZE) if ((BOARD_SIZE - 1 - col) % 2 == 0) else range(BOARD_SIZE - 1, -1, -1)
        for row in rows:
            positions.append((row, col))
    return positions


def spiral_clockwise(start_corner="top_left"):
    """Spiral pattern clockwise from specified corner."""
    positions = []
    visited = [[False] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    # Direction vectors: right, down, left, up
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    # Starting positions and direction indices for each corner
    corners = {
        "top_left": (0, 0, 0),      # start at (0,0), go right first
        "top_right": (0, BOARD_SIZE - 1, 1),   # start at (0,9), go down first
        "bottom_right": (BOARD_SIZE - 1, BOARD_SIZE - 1, 2),  # start at (9,9), go left first
        "bottom_left": (BOARD_SIZE - 1, 0, 3),  # start at (9,0), go up first
    }

    row, col, dir_idx = corners[start_corner]

    for _ in range(BOARD_SIZE * BOARD_SIZE):
        positions.append((row, col))
        visited[row][col] = True

        # Try to continue in current direction
        dr, dc = directions[dir_idx]
        new_row, new_col = row + dr, col + dc

        # If can't continue, turn clockwise
        if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and not visited[new_row][new_col]):
            dir_idx = (dir_idx + 1) % 4
            dr, dc = directions[dir_idx]
            new_row, new_col = row + dr, col + dc

        row, col = new_row, new_col

    return positions


def spiral_counterclockwise(start_corner="top_left"):
    """Spiral pattern counter-clockwise from specified corner."""
    positions = []
    visited = [[False] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    # Direction vectors: down, right, up, left (counter-clockwise from top-left)
    directions_map = {
        "top_left": [(1, 0), (0, 1), (-1, 0), (0, -1)],      # down, right, up, left
        "top_right": [(0, -1), (1, 0), (0, 1), (-1, 0)],     # left, down, right, up
        "bottom_right": [(-1, 0), (0, -1), (1, 0), (0, 1)],  # up, left, down, right
        "bottom_left": [(0, 1), (-1, 0), (0, -1), (1, 0)],   # right, up, left, down
    }

    corners = {
        "top_left": (0, 0),
        "top_right": (0, BOARD_SIZE - 1),
        "bottom_right": (BOARD_SIZE - 1, BOARD_SIZE - 1),
        "bottom_left": (BOARD_SIZE - 1, 0),
    }

    row, col = corners[start_corner]
    directions = directions_map[start_corner]
    dir_idx = 0

    for _ in range(BOARD_SIZE * BOARD_SIZE):
        positions.append((row, col))
        visited[row][col] = True

        dr, dc = directions[dir_idx]
        new_row, new_col = row + dr, col + dc

        if not (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and not visited[new_row][new_col]):
            dir_idx = (dir_idx + 1) % 4
            dr, dc = directions[dir_idx]
            new_row, new_col = row + dr, col + dc

        row, col = new_row, new_col

    return positions


def diagonal_wave(start_corner="top_left"):
    """Diagonal wave pattern from specified corner."""
    positions = []

    if start_corner == "top_left":
        # Diagonals from top-left to bottom-right
        for diag in range(2 * BOARD_SIZE - 1):
            for row in range(BOARD_SIZE):
                col = diag - row
                if 0 <= col < BOARD_SIZE:
                    positions.append((row, col))
    elif start_corner == "top_right":
        # Diagonals from top-right to bottom-left
        for diag in range(2 * BOARD_SIZE - 1):
            for row in range(BOARD_SIZE):
                col = BOARD_SIZE - 1 - diag + row
                if 0 <= col < BOARD_SIZE:
                    positions.append((row, col))
    elif start_corner == "bottom_left":
        # Diagonals from bottom-left to top-right
        for diag in range(2 * BOARD_SIZE - 1):
            for row in range(BOARD_SIZE - 1, -1, -1):
                col = diag - (BOARD_SIZE - 1 - row)
                if 0 <= col < BOARD_SIZE:
                    positions.append((row, col))
    elif start_corner == "bottom_right":
        # Diagonals from bottom-right to top-left
        for diag in range(2 * BOARD_SIZE - 1):
            for row in range(BOARD_SIZE - 1, -1, -1):
                col = BOARD_SIZE - 1 - diag + (BOARD_SIZE - 1 - row)
                if 0 <= col < BOARD_SIZE:
                    positions.append((row, col))

    return positions


def from_center():
    """Expanding squares from center to edges."""
    positions = []
    center = BOARD_SIZE // 2

    # For even board size, center is 4 tiles
    if BOARD_SIZE % 2 == 0:
        # Start with center 4 tiles
        positions.extend([(center - 1, center - 1), (center - 1, center),
                         (center, center - 1), (center, center)])
        added = {(center - 1, center - 1), (center - 1, center),
                (center, center - 1), (center, center)}

        # Expand outward
        for ring in range(1, center + 1):
            ring_positions = []
            for row in range(center - 1 - ring, center + 1 + ring):
                for col in range(center - 1 - ring, center + 1 + ring):
                    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                        if (row, col) not in added:
                            ring_positions.append((row, col))
                            added.add((row, col))
            # Sort ring positions for smooth appearance
            ring_positions.sort(key=lambda p: (abs(p[0] - center + 0.5) + abs(p[1] - center + 0.5)))
            positions.extend(ring_positions)
    else:
        # For odd board size
        positions.append((center, center))
        added = {(center, center)}

        for ring in range(1, center + 1):
            ring_positions = []
            for row in range(center - ring, center + ring + 1):
                for col in range(center - ring, center + ring + 1):
                    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                        if (row, col) not in added:
                            ring_positions.append((row, col))
                            added.add((row, col))
            ring_positions.sort(key=lambda p: (abs(p[0] - center) + abs(p[1] - center)))
            positions.extend(ring_positions)

    return positions


def to_center():
    """Contracting squares from edges to center."""
    return list(reversed(from_center()))


def random_order():
    """Random order of tile appearance."""
    positions = [(row, col) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)]
    random.shuffle(positions)
    return positions


# List of all available patterns with their names
ALL_PATTERNS = [
    ("snake_rows", snake_by_rows),
    ("snake_rows_reverse", snake_by_rows_reverse),
    ("snake_rows_alt", lambda: snake_by_rows(reverse_start=True)),
    ("snake_cols", snake_by_cols),
    ("snake_cols_reverse", snake_by_cols_reverse),
    ("snake_cols_alt", lambda: snake_by_cols(reverse_start=True)),
    ("spiral_cw_top_left", lambda: spiral_clockwise("top_left")),
    ("spiral_cw_top_right", lambda: spiral_clockwise("top_right")),
    ("spiral_cw_bottom_right", lambda: spiral_clockwise("bottom_right")),
    ("spiral_cw_bottom_left", lambda: spiral_clockwise("bottom_left")),
    ("spiral_ccw_top_left", lambda: spiral_counterclockwise("top_left")),
    ("spiral_ccw_top_right", lambda: spiral_counterclockwise("top_right")),
    ("spiral_ccw_bottom_right", lambda: spiral_counterclockwise("bottom_right")),
    ("spiral_ccw_bottom_left", lambda: spiral_counterclockwise("bottom_left")),
    ("diagonal_top_left", lambda: diagonal_wave("top_left")),
    ("diagonal_top_right", lambda: diagonal_wave("top_right")),
    ("diagonal_bottom_left", lambda: diagonal_wave("bottom_left")),
    ("diagonal_bottom_right", lambda: diagonal_wave("bottom_right")),
    ("from_center", from_center),
    ("to_center", to_center),
    ("random", random_order),
]


def get_random_pattern():
    """Returns a random pattern function and its name."""
    name, pattern_func = random.choice(ALL_PATTERNS)
    return name, pattern_func()
