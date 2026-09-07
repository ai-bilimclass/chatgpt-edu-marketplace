# Контракт практического учебного эпизода

**Статус: методическая рекомендация.** Контракт используется внутренне при создании нового или существенно изменяемого ҚМЖ/КСП. В таблицу плана переносить только понятные учителю поля, не печатать YAML как технический отчёт.

## Границы содержания

До выбора приёма зафиксировать:

```yaml
content_boundaries:
  previously_learned: []
  introduced_in_this_lesson: []
  deferred_content: []
  prohibited_assumptions: []
  allowed_example_types: []
  unknowns: []
  source_refs: []
```

- `previously_learned` не заполнять по предположению: использовать данные учителя, планирование или явно указанную связь с предыдущим уроком.
- `introduced_in_this_lesson` ограничить содержанием, необходимым для точной цели.
- `deferred_content` защищает урок от преждевременного расширения темы.
- `prohibited_assumptions` перечисляет сведения, которые нельзя считать установленными без источника.
- `unknowns` не скрывать: они ведут к уточнению, безопасной оговорке или ограничению результата.

## Схема эпизода

```yaml
practical_episode:
  episode_id: "episode-01"
  objective_refs: []
  stage: ""
  duration_minutes: 0
  thinking_process: ""
  technique_id: ""
  technique_reason: ""
  interaction_id: "individual"
  purpose: ""
  prerequisites: []
  teacher_instruction: ""
  task_content: ""
  student_actions: []
  individual_evidence: ""
  expected_response: ""
  acceptable_variations: []
  likely_misconceptions: []
  feedback_and_retry: ""
  next_teacher_action_if_met: ""
  next_teacher_action_if_not_met: ""
  support: []
  extension: []
  resources: []
  source_refs: []
  validation_status: "PASS | REVISE | LIMITATION"
  limitations: []
```

## Требования

1. `thinking_process` содержит ровно один основной код из восьми функций стартового каталога.
2. `technique_id` должен существовать в `practical-techniques-index.md`; условный приём требует заполненного `technique_reason` и выполненных условий применения.
3. `interaction_id` выбирается отдельно по `interaction-structures.md`; допустимо `individual` без дополнительной структуры.
4. `teacher_instruction` должна быть готовой к произнесению или размещению в документе: что сделать, с чем, в каком формате и за какое время.
5. `individual_evidence` должно позволять проверить достижение каждым учеником, в том числе при парной или групповой работе.
6. `expected_response` содержит ответ, модель решения или наблюдаемые признаки допустимого результата; `acceptable_variations` не расширяют цель произвольно.
7. Ошибка ведёт к содержательной обратной связи, действию ученика и повторной проверке, а не только к отметке или похвале.
8. Сумма длительности эпизодов вместе с переходами должна помещаться в урок.
9. При отсутствии необходимых данных ставить `LIMITATION`; не заполнять неизвестное правдоподобной выдумкой.

## Порядок сборки

`точная цель → границы содержания → этап → мыслительная функция → приём → структура взаимодействия → инструкция → индивидуальное доказательство → критерий/ожидаемый ответ → обратная связь и повторная попытка → следующее решение учителя`.
