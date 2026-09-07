from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCHOOL = ROOT.parents[1]


def read(path):
    return path.read_text(encoding="utf-8")


class MethodologyArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = read(ROOT / "references" / "methodology-core.md")
        cls.router = read(ROOT / "references" / "methodology-router.md")
        cls.handoff = read(SCHOOL / "references" / "lesson-plan-handoff.md")
        cls.terms = read(SCHOOL / "references" / "methodology-terminology-trilingual.md")
        cls.audit = read(ROOT / "references" / "methodology-audit.md")
        cls.protocol = read(ROOT / "references" / "lesson-design-protocol.md")
        cls.kagan = read(ROOT / "references" / "methods" / "kagan-structures.md")
        cls.techniques = read(ROOT / "references" / "practical-techniques-index.md")
        cls.interactions = read(ROOT / "references" / "interaction-structures.md")
        cls.episode = read(ROOT / "references" / "practical-episode-contract.md")

    def test_six_core_and_three_specialized_directions_exist(self):
        for filename in (
            "ubd-wiggins-mctighe.md",
            "formative-assessment-wiliam.md",
            "rosenshine-principles.md",
            "visible-thinking-routines.md",
            "dialogic-teaching-alexander-mercer.md",
            "project-based-learning.md",
            "design-thinking.md",
            "inquiry-problem-based-learning.md",
        ):
            self.assertTrue((ROOT / "references" / "methods" / filename).is_file(), filename)
        self.assertIn("Шесть основных направлений", self.router)
        self.assertIn("Три специализированных направления", self.router)

    def test_tools_and_foundations_are_not_universal_methods(self):
        self.assertIn("только инструменты и форматы", self.router)
        self.assertIn("только для обоснования конкретного решения", self.router)
        for filename in ("kagan-structures.md", "flipped-learning.md", "liljedahl-thinking-classrooms.md", "evidence-and-professional-foundations.md"):
            self.assertTrue((ROOT / "references" / "methods" / filename).is_file(), filename)

    def test_methodology_handoff_is_complete(self):
        for field in (
            "pedagogical_task",
            "learning_stage",
            "learner_difficulty",
            "core_method",
            "supporting_method",
            "specialized_method",
            "active_learning_methods",
            "learning_evidence",
            "formative_decision_points",
            "next_teacher_actions",
            "differentiation_and_accessibility",
        ):
            self.assertIn(field, self.handoff)

    def test_versioned_handoff_contains_release_two_contract(self):
        for field in (
            'schema_version: "2.0"', "lesson_content_version", "content_boundaries",
            "episodes", "canonical_tasks", "canonical_answers", "source_bindings",
            "validation_status", "unresolved_limitations", "derivative_registry",
        ):
            self.assertIn(field, self.handoff)
        self.assertIn('status: "requires_regeneration"', self.handoff)
        self.assertIn("контракт версии 1", self.handoff)

    def test_handoff_maps_episodes_to_derivative_materials(self):
        for field in ("worksheet_task_id", "slide_id", "source_lesson_content_version"):
            self.assertIn(field, self.handoff)
        self.assertIn("episode_id → worksheet_task_id", self.handoff)
        self.assertIn("episode_id → slide_id", self.handoff)

    def test_same_chat_continuity_notice_is_non_blocking_and_monolingual(self):
        self.assertIn("continuity_notice_shown", self.handoff)
        self.assertIn("Бір сынып пен бір пәнге арналған", self.handoff)
        self.assertIn("для одного класса и одного предмета", self.handoff)
        self.assertIn("for the same class and subject", self.handoff)
        self.assertIn("не показывать три языковые версии одновременно", self.handoff)
        self.assertIn("не просить согласия, подтверждения", self.handoff)
        self.assertIn("Не утверждать, что план сохранён в постоянной памяти", self.handoff)

    def test_required_trilingual_terms_exist(self):
        for term in (
            "Active Learning Methods",
            "Pedagogical Task",
            "Core Method",
            "Supporting Method",
            "Specialized Method",
            "Dialogic Teaching",
            "Differentiation and Accessibility",
            "Formative Decision Point",
            "Next Teacher Action",
        ):
            self.assertIn(term, self.terms)

    def test_audit_name_is_correct(self):
        self.assertTrue(self.audit.startswith("# Аудит методического качества"))

    def test_kagan_card_requires_all_pies_conditions(self):
        for condition in (
            "Positive Interdependence",
            "Individual Accountability",
            "Equal Participation",
            "Simultaneous Interaction",
        ):
            self.assertIn(condition, self.kagan)

    def test_specialized_boundaries_are_explicit(self):
        self.assertIn("Границы специализированных направлений", self.router)
        for boundary in ("Стартовая точка", "Основной процесс", "Обычная длительность", "Обязательный результат", "Основной риск"):
            self.assertIn(boundary, self.router)

    def test_integrated_cycle_and_extended_audit_exist(self):
        self.assertIn("интеграционный цикл", self.protocol)
        self.assertIn("15. **Рефлексия учителя:**", self.protocol)
        self.assertIn("Метапознание, закрепление и перенос", self.audit)
        self.assertIn("Ресурсы, цифровая среда и профессиональная этика", self.audit)

    def test_eight_thinking_functions_exist(self):
        for function_id in (
            "understand_and_model", "retrieve_and_check", "compare_and_classify",
            "argue_and_evaluate", "read_and_transform", "apply_and_solve",
            "investigate_and_create", "analyze_and_improve",
        ):
            self.assertIn(function_id, self.techniques)

    def test_catalog_has_twelve_universal_and_five_conditional_techniques(self):
        universal = (
            "model-guided-independent", "think-aloud", "retrieval-no-prompt",
            "explain-own-words", "comparison-table", "claim-evidence-reasoning",
            "example-counterexample", "predict-test-explain", "real-life-task",
            "find-explain-error", "criteria-check-revise", "exit-ticket",
        )
        conditional = ("jigsaw", "scamper", "pops", "venn-diagram", "case-method")
        for technique_id in universal + conditional:
            self.assertIn(f"`{technique_id}`", self.techniques)
        self.assertIn("12 универсальных приёмов", self.techniques)
        self.assertIn("5 условных приёмов", self.techniques)

    def test_interaction_structures_are_separate_and_accountable(self):
        for structure_id in ("think-pair-share", "peer-teaching", "learning-stations", "gallery-walk"):
            self.assertIn(structure_id, self.interactions)
        self.assertIn("не является мыслительной функцией", self.interactions)
        self.assertIn("индивидуальное доказательство", self.interactions.lower())

    def test_practical_episode_contract_is_complete(self):
        for field in (
            "content_boundaries", "episode_id", "objective_refs", "thinking_process",
            "technique_id", "interaction_id", "teacher_instruction", "student_actions",
            "individual_evidence", "expected_response", "likely_misconceptions",
            "feedback_and_retry", "next_teacher_action_if_met",
            "next_teacher_action_if_not_met", "validation_status", "limitations",
        ):
            self.assertIn(field, self.episode)
        self.assertIn("PASS | REVISE | LIMITATION", self.episode)


if __name__ == "__main__":
    unittest.main()
