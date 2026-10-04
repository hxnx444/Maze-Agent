

REASONS = {
    "EASY": (
        "BFS",
        "The maze was classified EASY, so the search space is small enough "
        "that BFS finds the goal with little overhead - the Manhattan-distance "
        "heuristic A* uses wouldn't meaningfully reduce work here.",
    ),
    "MEDIUM": (
        "A*",
        "The maze was classified MEDIUM, so a heuristic starts to pay off: "
        "A* is expected to expand noticeably fewer nodes than BFS.",
    ),
    "HARD": (
        "A*",
        "The maze was classified HARD (large/dense with a long start-goal "
        "distance), so BFS would expand a large fraction of the grid. A*'s "
        "Manhattan-distance heuristic keeps the search focused toward the goal.",
    ),
}


def decide(prediction):
   
    label = prediction["label"]
    algo_name, reason = REASONS.get(label, REASONS["MEDIUM"])
    return {
        "algorithmKey": "bfs" if algo_name == "BFS" else "astar",
        "algorithm": algo_name,
        "difficulty": label,
        "confidence": prediction["confidence"],
        "reason": reason,
    }
