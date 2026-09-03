export function buildTeacherNotes({
  purpose,
  script,
  instruction = "—",
  expectedAnswer = "—",
  assessment = "—",
  time = "—",
  support = "—",
  extension = "—",
  inclusiveSupport = "—",
  safety = "не требуется",
  sources = [],
}) {
  const sourceLines = sources.length ? sources.map((item) => `- ${item}`).join("\n") : "- Материалы учителя: не использованы";
  return [
    `Цель показа: ${purpose}`,
    `Сценарий учителя: ${script}`,
    `Инструкция: ${instruction}`,
    `Ожидаемый ответ / ключ: ${expectedAnswer}`,
    `Формативное оценивание: ${assessment}`,
    `Время: ${time}`,
    `Поддержка: ${support}`,
    `Усложнение: ${extension}`,
    `Инклюзивная поддержка: ${inclusiveSupport}`,
    `Безопасность: ${safety}`,
    "[Sources]",
    sourceLines,
  ].join("\n");
}

export function setTeacherNotes(slide, fields) {
  slide.speakerNotes.textFrame.setText(buildTeacherNotes(fields));
  slide.speakerNotes.setVisible(true);
}
