"""Canonical scored-descriptor validation shared by lesson and worksheet paths."""

from copy import deepcopy


def scoring(task):
    items = task.get("descriptor_scores")
    if not isinstance(items, list) or not items:
        raise ValueError("descriptor_scores required; explicitly complete legacy data, never invent points")
    for item in items:
        if (not isinstance(item, dict) or not isinstance(item.get("text"), str)
                or not item["text"].strip() or type(item.get("points")) is not int
                or item["points"] <= 0):
            raise ValueError("Each descriptor needs observable text and positive integer points")
    total = sum(item["points"] for item in items)
    if "total_points" in task and (type(task["total_points"]) is not int or task["total_points"] != total):
        raise ValueError("total_points must equal descriptor sum")
    support = task.get("support", "")
    if not isinstance(support, str):
        raise ValueError("support must be text")
    return {"descriptor_scores": deepcopy(items), "total_points": total, "support": support}
