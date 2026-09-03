# ҚМЖ/КСП handoff для производных материалов

Рабочий, практический или лабораторный лист и новая презентация создаются только на основе готового ҚМЖ/КСП/Lesson Plan.

Допустимы два источника:

1. прикреплённый учителем файл плана урока в читаемом формате;
2. подтверждённый учителем план урока, созданный плагином в текущем чате и переданный как `lesson_plan_handoff`.

Само наличие темы, цели, КТП или краткого описания урока не заменяет готовый план. План из другого чата повторно не восстанавливать по памяти: попросить прикрепить файл.

## Контракт handoff

После успешного создания и явного подтверждения плана урока сохранить внутренний пакет:

```yaml
lesson_plan_handoff:
  source: "same_chat_generated_lesson_plan"
  approved_by_teacher: true
  artifact_path: ""
  grade: ""
  subject: ""
  instruction_language: ""
  document_language: ""
  topic: ""
  duration_minutes: ""
  learning_objectives: []
  assessment_criteria: []
  lesson_stages: []
  required_tasks: []
  expected_answers: []
  formative_assessment: []
  support_and_extension: []
  homework: ""
  sources: []
  methodology:
    pedagogical_task: ""
    learning_stage: ""
    learner_difficulty: ""
    core_method: ""
    supporting_method: ""
    specialized_method: ""
    active_learning_methods: []
    student_actions: []
    learning_evidence: []
    formative_decision_points: []
    next_teacher_actions: []
    differentiation_and_accessibility: []
```

`approved_by_teacher: true` устанавливать только после явного подтверждения конкретной версии учителем. Черновик, автоматически созданный файл или отсутствие возражения не считать подтверждением.

Производный навык принимает пакет без повторной загрузки файла, если он относится к текущему чату, полный для запрошенного продукта и не существует более новой или противоречащей версии плана. Иначе запросить файл или подтверждение.

После приёма пакета не спрашивать повторно класс, предмет, язык, тему, продолжительность и точные цели. Одним сообщением запросить только параметры, специфичные для нового материала.

Блок `methodology` формирует только `school-lesson-planner` по [центральному методическому маршрутизатору](../skills/school-lesson-planner/references/methodology-router.md). Производный навык применяет подтверждённое решение и не выбирает другую основную методику. Пустой `supporting_method` или `specialized_method` допустим. Если прикреплённый план не содержит явной методической модели, производный навык не должен придумывать её: использовать только зафиксированные этапы, задания, критерии и доказательства.
