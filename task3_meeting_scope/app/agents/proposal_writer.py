def render_proposal(client_name: str, tasks: list[dict], total_hours: float, total_cost: float) -> str:
    rows = "\n".join(
        f"| {task['title'].replace('|', '/')} | {task['estimated_hours']:.1f} | {task['complexity']} | ${task['cost']:.2f} |"
        for task in tasks
    )
    return (
        f"# Statement of Work - {client_name}\n\n"
        "## Proposed deliverables\n\n"
        "| Deliverable | Hours | Complexity | Estimate |\n"
        "|---|---:|---|---:|\n"
        f"{rows}\n\n"
        "## Estimate summary\n\n"
        f"- Estimated effort: **{total_hours:.1f} hours**\n"
        f"- Estimated services: **${total_cost:,.2f}**\n\n"
        "This preliminary estimate is subject to requirements validation and written approval. "
        "Items identified as requiring review are not a commitment to custom development.\n"
    )

