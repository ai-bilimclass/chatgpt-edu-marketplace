#!/usr/bin/env python3
"""Scenario tests for validate_blueprint.py."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path


VALIDATOR = Path(__file__).with_name("validate_blueprint.py")


def task(
    number: int,
    bloom: str = "применение",
    score: int | None = None,
    descriptors: bool = True,
) -> dict:
    item = {
        "number": number,
        "bloom": bloom,
        "format": "short_answer",
        "objective_refs": ["LO1"],
        "minutes": 5,
    }
    if descriptors:
        item["descriptors"] = ["выполняет проверяемое действие"]
    if score is not None:
        item["score"] = score
    return item


def blueprint(assessment_type: str, grade: int, tasks: list[dict]) -> dict:
    return {
        "assessment_type": assessment_type,
        "grade": grade,
        "subject": "Математика",
        "language": "ru",
        "learning_objectives": [{"id": "LO1", "text": "Проверяемая цель"}],
        "task_count": len(tasks),
        "tasks": tasks,
        "time_minutes": max(10, 5 * len(tasks)),
    }


def run_case(name: str, data: dict, expected_code: int, contains: str) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / f"{name}.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    output = result.stdout + result.stderr
    if result.returncode != expected_code or contains not in output:
        raise AssertionError(
            f"{name}: code={result.returncode}, expected={expected_code}, "
            f"missing={contains!r}\n{output}"
        )
    print(f"PASS {name}")


def main() -> int:
    grade1 = blueprint("PRACTICE", 1, [task(1, "понимание")])
    run_case("grade1_practice", grade1, 0, "OK: grade 1 PRACTICE")

    primary_fo = blueprint("FO", 3, [task(1, "анализировать")])
    primary_fo["formative_scale_max"] = 10
    run_case("primary_fo", primary_fo, 0, "OK: primary FO")

    interim = blueprint("INTERIM", 4, [task(1, score=8), task(2, score=8)])
    interim["max_score"] = 16
    run_case("primary_interim", interim, 0, "OK: INTERIM")

    secondary_fo = blueprint("FO", 7, [task(1, "оценивать")])
    run_case("secondary_fo", secondary_fo, 0, "OK: FO")

    sor = blueprint("SOR", 7, [task(1, score=4), task(2, score=4)])
    sor["max_score"] = 8
    run_case("sor", sor, 0, "OK: SOR")

    soch = blueprint(
        "SOCh", 10,
        [task(number, "создавать", 1, descriptors=False) for number in range(1, 11)],
    )
    formats = [
        "alternative_choice", "multiple_choice", "multiple_response",
        "multiple_identification", "completion", "short_answer", "matching",
        "sequencing", "short_answer", "multiple_choice",
    ]
    for item, task_format in zip(soch["tasks"], formats):
        item["format"] = task_format
    soch["max_score"] = 10
    soch["specification_task_count"] = 10
    soch["weekly_hours"] = 2
    soch["grade_reporting_period"] = "quarter"
    run_case("soch_draft", soch, 0, "WARNING: SOCh has no technical_specification")

    project_soch = blueprint(
        "SOCh", 10,
        [task(number, score=1, descriptors=False) for number in range(1, 7)],
    )
    project_soch["max_score"] = 6
    project_soch["weekly_hours"] = 2
    project_soch["grade_reporting_period"] = "quarter"
    run_case("soch_project_count_allowed", project_soch, 0, "label output as a draft")

    invalid = copy.deepcopy(project_soch)
    invalid["specification_task_count"] = 8
    run_case("soch_specification_count_mismatch", invalid, 1, "does not match specification_task_count")

    invalid = copy.deepcopy(soch)
    invalid["tasks"][0]["descriptors"] = ["лишний дескриптор"]
    run_case("soch_descriptors_rejected", invalid, 1, "unless the specification requires them")

    with_spec_descriptors = copy.deepcopy(soch)
    with_spec_descriptors["technical_specification"] = "teacher-specification.pdf"
    with_spec_descriptors["soch_descriptors_required"] = True
    for item in with_spec_descriptors["tasks"]:
        item["descriptors"] = ["specified observable element"]
    run_case("soch_specification_descriptors_allowed", with_spec_descriptors, 0, "OK: SOCh")

    invalid = copy.deepcopy(grade1)
    invalid["assessment_type"] = "FO"
    run_case("grade1_fo_rejected", invalid, 1, "grade 1 allows only")

    invalid = copy.deepcopy(primary_fo)
    invalid["tasks"][0]["score"] = 10
    run_case("primary_fo_task_score_rejected", invalid, 1, "scoreless tasks")

    invalid = copy.deepcopy(secondary_fo)
    invalid["max_score"] = 10
    run_case("secondary_fo_score_rejected", invalid, 1, "must not contain scores")

    invalid = copy.deepcopy(sor)
    invalid["max_score"] = 7
    run_case("sor_sum_rejected", invalid, 1, "task score sum=8")

    invalid = copy.deepcopy(secondary_fo)
    invalid["tasks"][0].pop("descriptors")
    run_case("missing_descriptors_rejected", invalid, 1, "descriptors must be")

    invalid = copy.deepcopy(secondary_fo)
    invalid["language"] = "de"
    run_case("invalid_language_rejected", invalid, 1, "language must be ru, kk, or en")

    english = copy.deepcopy(secondary_fo)
    english["language"] = "en"
    run_case("english_language_allowed", english, 0, "OK: FO")

    invalid = copy.deepcopy(secondary_fo)
    invalid["time_minutes"] = "15"
    run_case("invalid_time_type_rejected", invalid, 1, "time_minutes must be")

    invalid = copy.deepcopy(secondary_fo)
    invalid["tasks"][0].pop("number")
    run_case("missing_task_number_rejected", invalid, 1, "number must be a positive integer")

    invalid = copy.deepcopy(secondary_fo)
    invalid["tasks"][0]["format"] = "essay"
    run_case("invalid_task_format_rejected", invalid, 1, "format must be one of")

    invalid = copy.deepcopy(primary_fo)
    invalid["planning_scope"] = "lesson"
    run_case("invalid_planning_scope_rejected", invalid, 1, "planning_scope must be")

    invalid = copy.deepcopy(sor)
    invalid.pop("max_score")
    run_case("missing_sor_max_score_rejected", invalid, 1, "requires a positive max_score")

    invalid = copy.deepcopy(secondary_fo)
    invalid["task_count"] = True
    run_case("boolean_task_count_rejected", invalid, 1, "task_count must be")

    exempt_cases = [
        ("music_grade6_sor_rejected", "Музыка", 6, {}),
        ("art_grade9_sor_rejected", "Көркем еңбек", 9, {}),
        ("pe_grade11_sor_rejected", "Физическая культура", 11, {}),
        ("religion_grade9_sor_rejected", "Светскость и основы религиоведения", 9, {}),
        ("business_grade10_sor_rejected", "Основы предпринимательства и бизнеса", 10, {}),
        ("graphics_grade10_sor_rejected", "Графика и проектирование", 10, {}),
        ("nvp_grade10_sor_rejected", "НВП", 10, {}),
        ("variative_grade8_sor_rejected", "Робототехника", 8, {"curriculum_component": "variative"}),
    ]
    for name, subject, grade, extra in exempt_cases:
        invalid = copy.deepcopy(sor)
        invalid["subject"] = subject
        invalid["grade"] = grade
        invalid.update(extra)
        run_case(name, invalid, 1, "is prohibited")

    music_grade7 = copy.deepcopy(sor)
    music_grade7["subject"] = "Музыка"
    music_grade7["grade"] = 7
    run_case("music_grade7_sor_allowed", music_grade7, 0, "OK: SOR")

    trainee = copy.deepcopy(secondary_fo)
    trainee["teacher_experience_level"] = "trainee"
    run_case("teacher_trainee_allowed", trainee, 0, "OK: FO")

    invalid = copy.deepcopy(secondary_fo)
    invalid["teacher_experience_level"] = "intern"
    run_case("invalid_teacher_level_rejected", invalid, 1, "teacher_experience_level must be")

    one_hour_soch = copy.deepcopy(soch)
    one_hour_soch["weekly_hours"] = 1
    one_hour_soch["annual_hours"] = 34
    one_hour_soch["grade_reporting_period"] = "semester"
    run_case("one_hour_soch_rejected", one_hour_soch, 1, "do not create SOCh")

    missing_hours_soch = copy.deepcopy(soch)
    missing_hours_soch.pop("weekly_hours")
    run_case("soch_requires_weekly_hours", missing_hours_soch, 1, "requires weekly_hours")

    one_hour_sor = copy.deepcopy(sor)
    one_hour_sor["weekly_hours"] = 1
    one_hour_sor["annual_hours"] = 34
    one_hour_sor["grade_reporting_period"] = "semester"
    one_hour_sor["sor_count_in_quarter"] = 2
    run_case("one_hour_sor_allowed", one_hour_sor, 0, "OK: SOR")

    invalid = copy.deepcopy(one_hour_sor)
    invalid["grade_reporting_period"] = "quarter"
    run_case("one_hour_requires_semester_reporting", invalid, 1, "requires grade_reporting_period=semester")

    invalid = copy.deepcopy(one_hour_sor)
    invalid["sor_count_in_quarter"] = 3
    run_case("one_hour_sor_limit", invalid, 1, "sor_count_in_quarter must be")

    exempt_soch = copy.deepcopy(soch)
    exempt_soch["subject"] = "Музыка"
    exempt_soch["grade"] = 6
    run_case("subject_exemption_precedes_hour_rule", exempt_soch, 1, "is prohibited")

    print("All scenario tests passed: 40/40")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
