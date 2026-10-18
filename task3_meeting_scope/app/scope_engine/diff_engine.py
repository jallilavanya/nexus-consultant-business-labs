def compare_scope(baseline: list[dict], updated: list[dict]) -> dict:
    old_by_title = {task["title"].casefold(): task for task in baseline}
    new_by_title = {task["title"].casefold(): task for task in updated}
    added = [task for key, task in new_by_title.items() if key not in old_by_title]
    removed = [task for key, task in old_by_title.items() if key not in new_by_title]
    modified = [
        {"before": old_by_title[key], "after": task}
        for key, task in new_by_title.items()
        if key in old_by_title and task != old_by_title[key]
    ]
    return {
        "new_tasks": added,
        "modified_tasks": modified,
        "removed_tasks": removed,
        "out_of_scope_items": added,
        "markdown": _render(added, modified, removed),
    }


def _render(added: list[dict], modified: list[dict], removed: list[dict]) -> str:
    def bullets(items):
        return "\n".join(f"- {item.get('title', 'Untitled')}" for item in items) or "- None"

    changes = "\n".join(
        f"- {item['before']['title']}: {item['before']['estimated_hours']}h -> "
        f"{item['after']['estimated_hours']}h"
        for item in modified
    ) or "- None"
    return (
        "## Scope delta\n\n### New Tasks\n" + bullets(added)
        + "\n\n### Modified Tasks\n" + changes
        + "\n\n### Removed Tasks\n" + bullets(removed)
        + "\n\n### Out-of-Scope Items (Extra Cost)\n" + bullets(added)
    )

