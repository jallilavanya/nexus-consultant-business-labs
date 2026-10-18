import math


def estimate(requirement: str, product_fit: str) -> dict:
    words = len(requirement.split())
    integration = any(word in requirement.lower() for word in ("integrat", "sync", "api", "migrat"))
    complexity = "high" if integration or words > 28 else "medium" if words > 14 else "low"
    base = {"low": 4, "medium": 12, "high": 28}[complexity]
    hours = 1.0 if product_fit == "built_in" else float(math.ceil(base * (1 + max(0, words - 12) / 30)))
    if product_fit == "built_in":
        complexity = "low"
    return {
        "title": requirement[:100],
        "description": requirement,
        "product_fit": product_fit,
        "estimated_hours": hours,
        "complexity": complexity,
    }

