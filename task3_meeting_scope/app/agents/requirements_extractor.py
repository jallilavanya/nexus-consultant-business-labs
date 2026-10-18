import re


REQUEST_MARKERS = (
    "need", "want", "would like", "please", "must", "should", "require",
    "feature", "add ", "build ", "create ", "integrate", "automate",
)
PAIN_MARKERS = ("problem", "pain", "difficult", "manual", "slow", "can't", "cannot", "issue", "frustrat")


def extract_requirements(transcript: str) -> dict[str, list[str]]:
    sentences = [
        re.sub(r"\s+", " ", part).strip(" -*\t")
        for part in re.split(r"(?<=[.!?])\s+|\n+", transcript)
    ]
    sentences = [sentence for sentence in sentences if len(sentence) >= 12]
    requirements = _unique(
        sentence for sentence in sentences
        if any(marker in sentence.lower() for marker in REQUEST_MARKERS)
    )
    pain_points = _unique(
        sentence for sentence in sentences
        if any(marker in sentence.lower() for marker in PAIN_MARKERS)
    )
    if not requirements and sentences:
        requirements = sentences[:3]
    return {"requirements": requirements, "pain_points": pain_points}


def _unique(items):
    seen = set()
    result = []
    for item in items:
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

