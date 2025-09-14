KEYWORDS = [
    "you won't believe",
    "shocking",
    "what happens next",
    "top ",
    "reasons",
    "secret",
    "one weird trick",
]

def score_clickbait(title: str) -> float:
    """Toy heuristic for demo purposes; swap for a real model later."""
    t = title.lower()
    score = 0.0
    score += 0.3 if "!" in t else 0.0
    score += sum(0.15 for k in KEYWORDS if k in t)
    return min(score, 1.0)
