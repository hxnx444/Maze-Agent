

import heapq
import time
from collections import deque

from maze import neighbors4, manhattan


def _reconstruct_path(parent, start, goal, key):
    path = [dict(goal)]
    cur = goal
    while not (cur["r"] == start["r"] and cur["c"] == start["c"]):
        cur = parent[key(cur["r"], cur["c"])]
        path.append(dict(cur))
    path.reverse()
    return path


def run_bfs(maze):
    grid, rows, cols = maze["grid"], maze["rows"], maze["cols"]
    start, goal = maze["start"], maze["goal"]
    key = lambda r, c: r * cols + c

    visited = {key(start["r"], start["c"])}
    visited_order = []
    parent = {}

    queue = deque([start])

    t0 = time.perf_counter()
    found = False
    expanded = 0

    while queue:
        cur = queue.popleft()
        expanded += 1
        visited_order.append({"r": cur["r"], "c": cur["c"]})

        if cur["r"] == goal["r"] and cur["c"] == goal["c"]:
            found = True
            break

        for n in neighbors4(cur["r"], cur["c"], rows, cols):
            if grid[n["r"]][n["c"]] == 1:
                continue
            k = key(n["r"], n["c"])
            if k in visited:
                continue
            visited.add(k)
            parent[k] = cur
            queue.append(n)

    t1 = time.perf_counter()

    path = _reconstruct_path(parent, start, goal, key) if found else []

    return {
        "algorithm": "BFS",
        "found": found,
        "path": path,
        "visitedOrder": visited_order,
        "expanded": expanded,
        "timeMs": (t1 - t0) * 1000,
    }


def run_astar(maze):
    grid, rows, cols = maze["grid"], maze["rows"], maze["cols"]
    start, goal = maze["start"], maze["goal"]
    key = lambda r, c: r * cols + c

    g_score = {key(start["r"], start["c"]): 0}
    parent = {}
    closed = set()
    visited_order = []

    # heap items: (f, tie_breaker, r, c, g)
    counter = 0
    heap = [(manhattan(start, goal), counter, start["r"], start["c"], 0)]

    t0 = time.perf_counter()
    found = False
    expanded = 0

    while heap:
        f, _, r, c, g = heapq.heappop(heap)
        ck = key(r, c)
        if ck in closed:
            continue
        closed.add(ck)
        expanded += 1
        visited_order.append({"r": r, "c": c})

        if r == goal["r"] and c == goal["c"]:
            found = True
            break

        for n in neighbors4(r, c, rows, cols):
            if grid[n["r"]][n["c"]] == 1:
                continue
            nk = key(n["r"], n["c"])
            if nk in closed:
                continue

            tentative_g = g + 1
            if nk not in g_score or tentative_g < g_score[nk]:
                g_score[nk] = tentative_g
                parent[nk] = {"r": r, "c": c}
                new_f = tentative_g + manhattan(n, goal)
                counter += 1
                heapq.heappush(heap, (new_f, counter, n["r"], n["c"], tentative_g))

    t1 = time.perf_counter()

    path = _reconstruct_path(parent, start, goal, key) if found else []

    return {
        "algorithm": "A*",
        "found": found,
        "path": path,
        "visitedOrder": visited_order,
        "expanded": expanded,
        "timeMs": (t1 - t0) * 1000,
    }
