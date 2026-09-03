#!/usr/bin/env python3
"""Validate a Kazakhstan school assessment blueprint for consistency."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ALLOWED_TYPES = {"PRACTICE", "FO", "INTERIM", "SOR", "SOCh"}
ALLOWED_BLOOM = {
    "remember", "understand", "apply", "analyze", "evaluate", "create",
    "знание", "запоминание", "понимание", "применение", "анализ", "оценка", "создание",
    "анализировать", "оценивать", "создавать",
}
PRIMARY_INTERIM_MAX = {2: 12, 3: 14, 4: 16}
SUMMATIVE_EXEMPT_SUBJECTS = (
    ({"музыка", "music"}, range(5, 7)),
    ({"художественный труд", "көркем еңбек", "artistic labor", "arts and crafts"}, range(5, 10)),
    ({"физическая культура", "дене шынықтыру", "physical education"}, range(5, 12)),
    (
        {
            "светскость и основы религиоведения",
            "зайырлылық және дінтану негіздері",
            "secularism and fundamentals of religious studies",
        },
        range(9, 10),
    ),
    (
        {
            "основы предпринимательства и бизнеса",
            "кәсіпкерлік және бизнес негіздері",
            "fundamentals of entrepreneurship and business",
        },
        range(10, 12),
    ),
    ({"графика и проектирование", "графика және жобалау", "graphics and design"}, range(10, 12)),
    (
        {
            "начальная военная подготовка",
            "начальная военная и технологическая подготовка",
            "нвп",
            "нвтп",
            "алғашқы әскери дайындық",
            "алғашқы әскери және технологиялық дайындық",
            "initial military training",
        },
        range(10, 12),
    ),
)
ALLOWED_FORMATS = {
    "alternative_choice",
    "multiple_choice",
    "multiple_response",
    "multiple_identification",
    "completion",
    "short_answer",
    "matching",
    "sequencing",
}
ALLOWED_TEACHER_LEVELS = {"trainee", "beginner", "experienced", "methodologist"}
ALLOWED_REPORTING_PERIODS = {"quarter", "semester"}


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def objective_ids(items: object) -> set[str]:
    if not isinstance(items, list):
        return set()
    return {
        str(item.get("id")) if isinstance(item, dict) else str(item)
        for item in items
        if (isinstance(item, dict) and item.get("id") not in {None, ""})
        or (not isinstance(item, dict) and str(item).strip())
    }


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def normalize_policy_value(value: object) -> str:
    text = str(value or "").casefold().replace("ё", "е").replace("_", " ")
    text = re.sub(r"\([^)]*\)", " ", text)
    return " ".join(re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).split())


def summative_assessment_exemption_reason(data: dict, grade: int | None) -> str | None:
    academic_year = normalize_policy_value(data.get("academic_year", "2026–2027"))
    if academic_year != "2026 2027" or grade is None:
        return None
    component = normalize_policy_value(data.get("curriculum_component"))
    if component in {"variative", "вариативный", "вариативный компонент", "вариативтік компонент"}:
        if 5 <= grade <= 11:
            return "вариативный компонент, 5–11 классы"
    subject = normalize_policy_value(data.get("subject"))
    for aliases, grades in SUMMATIVE_EXEMPT_SUBJECTS:
        if subject in aliases and grade in grades:
            return f"{data.get('subject')}, {grade} класс"
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_blueprint.py BLUEPRINT.json", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON: {exc}")
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    required = [
        "assessment_type", "grade", "subject", "language",
        "learning_objectives", "task_count", "tasks",
    ]
    for key in required:
        if key not in data:
            fail(f"missing field: {key}", errors)

    assessment_type = data.get("assessment_type")
    if assessment_type not in ALLOWED_TYPES:
        fail("assessment_type must be PRACTICE, FO, INTERIM, SOR, or SOCh", errors)

    grade = data.get("grade")
    if not isinstance(grade, int) or isinstance(grade, bool) or not 1 <= grade <= 11:
        fail("grade must be an integer from 1 to 11", errors)
        grade = None

    subject = data.get("subject")
    if not isinstance(subject, str) or not subject.strip():
        fail("subject must be a non-empty string", errors)

    exemption_reason = summative_assessment_exemption_reason(data, grade)
    if assessment_type in {"SOR", "SOCh"} and exemption_reason:
        fail(
            f"{assessment_type} is prohibited for {exemption_reason} in 2026–2027; "
            "use formative/current assessment or credit criteria instead",
            errors,
        )

    language = data.get("language")
    if language not in {"ru", "kk", "en"}:
        fail("language must be ru, kk, or en", errors)

    teacher_level = data.get("teacher_experience_level", "trainee")
    if teacher_level not in ALLOWED_TEACHER_LEVELS:
        fail(
            "teacher_experience_level must be trainee, beginner, experienced, or methodologist",
            errors,
        )

    weekly_hours = data.get("weekly_hours")
    if weekly_hours is not None and (not is_number(weekly_hours) or weekly_hours <= 0):
        fail("weekly_hours must be a positive number", errors)
    annual_hours = data.get("annual_hours")
    if annual_hours is not None and (not is_number(annual_hours) or annual_hours <= 0):
        fail("annual_hours must be a positive number", errors)
    reporting_period = data.get("grade_reporting_period")
    if reporting_period is not None and reporting_period not in ALLOWED_REPORTING_PERIODS:
        fail("grade_reporting_period must be quarter or semester", errors)
    semester = data.get("semester")
    if semester is not None and semester not in {1, 2}:
        fail("semester must be 1 or 2", errors)
    sor_count = data.get("sor_count_in_quarter")
    if sor_count is not None and (
        not isinstance(sor_count, int) or isinstance(sor_count, bool) or not 0 <= sor_count <= 2
    ):
        fail("sor_count_in_quarter must be an integer from 0 to 2", errors)

    if assessment_type == "SOCh" and isinstance(grade, int) and 5 <= grade <= 11:
        if weekly_hours is None:
            fail("SOCh for grades 5-11 requires weekly_hours", errors)
        elif weekly_hours == 1:
            fail(
                "weekly_hours=1: do not create SOCh; the semester grade is based on FO and SOR",
                errors,
            )
    if weekly_hours == 1 and isinstance(grade, int) and 5 <= grade <= 11:
        if reporting_period != "semester":
            fail("weekly_hours=1 requires grade_reporting_period=semester", errors)

    if grade == 1 and assessment_type != "PRACTICE":
        fail("grade 1 allows only scoreless PRACTICE tasks with descriptors", errors)
    elif grade != 1 and assessment_type == "PRACTICE":
        fail("PRACTICE is reserved for grade 1", errors)
    elif grade in {2, 3, 4} and assessment_type not in {"FO", "INTERIM"}:
        fail("grades 2-4 allow only FO or INTERIM; do not create SOR or SOCh", errors)
    elif isinstance(grade, int) and 5 <= grade <= 11 and assessment_type == "INTERIM":
        fail("INTERIM is only for grades 2-4", errors)

    objectives = data.get("learning_objectives", [])
    if not isinstance(objectives, list) or not objectives:
        fail("learning_objectives must be a non-empty list", errors)
    elif len(objective_ids(objectives)) != len(objectives):
        fail("each learning objective must have a non-empty unique id", errors)

    tasks = data.get("tasks", [])
    task_count = data.get("task_count")
    if not isinstance(tasks, list):
        fail("tasks must be a list", errors)
        tasks = []
    if not isinstance(task_count, int) or isinstance(task_count, bool) or task_count <= 0:
        fail("task_count must be a positive integer", errors)
    elif task_count != len(tasks):
        fail(f"task_count={task_count}, but tasks contains {len(tasks)} items", errors)
    elif assessment_type == "SOCh":
        specification_task_count = data.get("specification_task_count")
        if specification_task_count is not None:
            if (
                not isinstance(specification_task_count, int)
                or isinstance(specification_task_count, bool)
                or specification_task_count <= 0
            ):
                fail("specification_task_count must be a positive integer", errors)
            elif task_count != specification_task_count:
                fail(
                    f"SOCh task_count={task_count} does not match "
                    f"specification_task_count={specification_task_count}",
                    errors,
                )

    is_formative = assessment_type == "FO"
    seen_numbers: set[object] = set()
    covered: set[str] = set()
    score_sum = 0.0
    time_sum = 0.0
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            fail(f"task {index} must be an object", errors)
            continue
        number = task.get("number")
        if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
            fail(f"task {index}: number must be a positive integer", errors)
        elif number in seen_numbers:
            fail(f"duplicate task number: {number}", errors)
        seen_numbers.add(number)

        bloom = str(task.get("bloom", "")).lower()
        if bloom not in ALLOWED_BLOOM:
            fail(f"task {number}: unsupported Bloom level '{bloom}'", errors)

        task_format = task.get("format")
        if task_format not in ALLOWED_FORMATS:
            allowed = ", ".join(sorted(ALLOWED_FORMATS))
            fail(f"task {number}: format must be one of: {allowed}", errors)

        refs = task.get("objective_refs", [])
        if not isinstance(refs, list) or not refs:
            fail(f"task {number}: objective_refs must be non-empty", errors)
        else:
            covered.update(str(ref) for ref in refs)

        descriptors = task.get("descriptors")
        if assessment_type == "SOCh":
            descriptors_required = data.get("soch_descriptors_required") is True
            if descriptors_required:
                if (
                    not isinstance(descriptors, list)
                    or not descriptors
                    or any(not isinstance(item, str) or not item.strip() for item in descriptors)
                ):
                    fail(f"task {number}: specification requires descriptors", errors)
            elif "descriptors" in task:
                fail(
                    f"task {number}: SOCh tasks must not contain descriptors unless "
                    "the specification requires them",
                    errors,
                )
        elif (
            not isinstance(descriptors, list)
            or not descriptors
            or any(not isinstance(item, str) or not item.strip() for item in descriptors)
        ):
            fail(f"task {number}: descriptors must be a non-empty list of strings", errors)

        if is_formative or assessment_type == "PRACTICE":
            if "score" in task:
                fail(f"task {number}: scoreless tasks must not assign a score", errors)
        else:
            score = task.get("score")
            if not is_number(score) or score <= 0:
                fail(f"task {number}: score must be positive", errors)
            else:
                score_sum += score

        minutes = task.get("minutes", 0)
        if not is_number(minutes) or minutes < 0:
            fail(f"task {number}: minutes must be non-negative", errors)
        else:
            time_sum += minutes

    assessed_objectives = objective_ids(objectives)
    missing_coverage = sorted(assessed_objectives - covered)
    unknown_refs = sorted(covered - assessed_objectives)
    if missing_coverage:
        fail("objectives without tasks: " + ", ".join(missing_coverage), errors)
    if unknown_refs:
        fail("unknown objective references: " + ", ".join(unknown_refs), errors)

    if assessment_type == "PRACTICE":
        if "max_score" in data or "formative_scale_max" in data:
            fail("grade 1 PRACTICE must not contain a score or score scale", errors)
    elif is_formative and grade in {2, 3, 4}:
        if "max_score" in data:
            fail("primary FO must not use max_score as a sum of task points", errors)
        if data.get("formative_scale_max") != 10:
            fail("primary FO requires formative_scale_max=10", errors)

        planning_scope = data.get("planning_scope", "single")
        if planning_scope not in {"single", "quarter"}:
            fail("planning_scope must be single or quarter", errors)
        quarter_objectives = objective_ids(data.get("quarter_learning_objectives"))
        if planning_scope == "quarter" and not quarter_objectives:
            fail("quarter FO planning requires quarter_learning_objectives", errors)
        if quarter_objectives:
            coverage = len(assessed_objectives & quarter_objectives) / len(quarter_objectives)
            if planning_scope == "quarter" and coverage < 0.5:
                fail(f"quarter FO objective coverage is {coverage:.0%}; minimum is 50%", errors)
            elif planning_scope != "quarter" and coverage < 0.5:
                warnings.append(
                    f"this FO covers {coverage:.0%} of quarter objectives; check cumulative quarter coverage"
                )
    elif is_formative:
        if "max_score" in data or "formative_scale_max" in data:
            fail("FO for grades 5-11 must not contain scores or a score scale", errors)

    if assessment_type == "INTERIM" and grade in PRIMARY_INTERIM_MAX:
        expected_max = PRIMARY_INTERIM_MAX[grade]
        if data.get("max_score") != expected_max:
            fail(f"grade {grade} INTERIM requires max_score={expected_max}", errors)
        if score_sum != expected_max:
            fail(f"grade {grade} INTERIM task score sum must be {expected_max}, got {score_sum:g}", errors)
    elif assessment_type in {"SOR", "SOCh"}:
        max_score = data.get("max_score")
        if not is_number(max_score) or max_score <= 0:
            fail(f"{assessment_type} requires a positive max_score", errors)
        elif max_score != score_sum:
            fail(f"max_score={max_score}, task score sum={score_sum:g}", errors)

    if "time_minutes" in data:
        time_minutes = data["time_minutes"]
        if not is_number(time_minutes) or time_minutes <= 0:
            fail("time_minutes must be a positive number", errors)
        elif time_minutes < time_sum:
            warnings.append(
                f"task time sum={time_sum:g} exceeds time_minutes={time_minutes:g}"
            )
    if assessment_type == "SOCh" and not data.get("technical_specification"):
        warnings.append("SOCh has no technical_specification; label output as a draft")

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    if not errors:
        if assessment_type == "PRACTICE":
            print(
                f"OK: grade 1 PRACTICE with {len(tasks)} tasks, descriptors, no points, "
                f"{len(assessed_objectives)} objectives covered"
            )
        elif is_formative and grade in {2, 3, 4}:
            print(
                f"OK: primary FO with {len(tasks)} tasks, 1-10 aggregate scale, "
                f"no task points, {len(assessed_objectives)} objectives covered"
            )
        elif is_formative:
            print(
                f"OK: FO with {len(tasks)} tasks, no points, "
                f"{len(assessed_objectives)} objectives covered"
            )
        else:
            print(
                f"OK: {assessment_type} with {len(tasks)} tasks, {score_sum:g} points, "
                f"{len(assessed_objectives)} objectives covered"
            )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
