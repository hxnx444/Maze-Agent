

import random

ROWS = 19
COLS = 25


def _in_bounds(r, c, rows, cols):
    return 0 < r < rows - 1 and 0 < c < cols - 1


def generate_maze(rows=ROWS, cols=COLS):
   
    grid = [[1 for _ in range(cols)] for _ in range(rows)]

    start = {"r": 1, "c": 1}
    goal = {"r": rows - 2, "c": cols - 2}

    stack = [dict(start)]
    grid[start["r"]][start["c"]] = 0

    dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        cur = stack[-1]
        shuffled = dirs[:]
        random.shuffle(shuffled)
        advanced = False

        for dr, dc in shuffled:
            nr, nc = cur["r"] + dr, cur["c"] + dc
            if _in_bounds(nr, nc, rows, cols) and grid[nr][nc] == 1:
                grid[cur["r"] + dr // 2][cur["c"] + dc // 2] = 0
                grid[nr][nc] = 0
                stack.append({"r": nr, "c": nc})
                advanced = True
                break

        if not advanced:
            stack.pop()

    
    grid[goal["r"]][goal["c"]] = 0


    extra_openings = int((rows * cols) * 0.02)
    for _ in range(extra_openings):
        r = 1 + random.randrange(rows - 2)
        c = 1 + random.randrange(cols - 2)
        if r % 2 == 1 and c % 2 == 0:
            grid[r][c] = 0
        elif r % 2 == 0 and c % 2 == 1:
            grid[r][c] = 0

    return {"grid": grid, "rows": rows, "cols": cols, "start": start, "goal": goal}


def neighbors4(r, c, rows, cols):
    out = []
    if r > 0:
        out.append({"r": r - 1, "c": c})
    if r < rows - 1:
        out.append({"r": r + 1, "c": c})
    if c > 0:
        out.append({"r": r, "c": c - 1})
    if c < cols - 1:
        out.append({"r": r, "c": c + 1})
    return out


def manhattan(a, b):
    return abs(a["r"] - b["r"]) + abs(a["c"] - b["c"])


def extract_features(maze):
    grid, rows, cols = maze["grid"], maze["rows"], maze["cols"]
    start, goal = maze["start"], maze["goal"]
    total_cells = rows * cols

    open_cells = 0
    wall_cells = 0
    dead_ends = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                open_cells += 1
                open_neighbors = sum(
                    1 for n in neighbors4(r, c, rows, cols) if grid[n["r"]][n["c"]] == 0
                )
                if open_neighbors == 1:
                    dead_ends += 1
            else:
                wall_cells += 1

    wall_density = wall_cells / total_cells
    distance = manhattan(start, goal)

    return {
        "size": total_cells,
        "wallDensity": wall_density,
        "distance": distance,
        "openCells": open_cells,
        "deadEnds": dead_ends,
    }
