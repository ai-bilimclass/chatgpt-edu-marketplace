import { FRAME, PT, textStyle } from "./theme.mjs";

function addText(slide, name, text, position, style) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = style;
  return shape;
}

function addHeader(slide, title, palette, number) {
  addText(slide, "slide-title", title, { left: FRAME.left, top: FRAME.top, width: 1020, height: 52 }, textStyle(PT.slideTitle, palette.dark, { bold: true }));
  addText(slide, "slide-number", String(number), { left: 1150, top: 52, width: 56, height: 28 }, textStyle(PT.caption, palette.dark, { bold: true }));
}

export function titleSlide(slide, { title, subtitle = "", palette }) {
  slide.background.fill = palette.paper;
  addText(slide, "deck-title", title, { left: 86, top: 174, width: 850, height: 180 }, textStyle(PT.deckTitle, palette.dark, { bold: true }));
  if (subtitle) addText(slide, "deck-subtitle", subtitle, { left: 90, top: 382, width: 820, height: 80 }, textStyle(PT.subhead, palette.ink));
}

export function objectivesSlide(slide, { title, objectives, criteria, palette, number }) {
  slide.background.fill = palette.paper;
  addHeader(slide, title, palette, number);
  addText(slide, "objectives", objectives.map((x) => `• ${x}`).join("\n"), { left: 70, top: 138, width: 530, height: 440 }, textStyle(PT.body, palette.ink));
  addText(slide, "criteria", criteria.map((x) => `✓ ${x}`).join("\n"), { left: 660, top: 138, width: 520, height: 440 }, textStyle(PT.body, palette.dark));
}

export function promptSlide(slide, { title, prompt, cues = [], palette, number }) {
  slide.background.fill = palette.paper;
  addHeader(slide, title, palette, number);
  addText(slide, "prompt", prompt, { left: 120, top: 178, width: 1040, height: 170 }, textStyle(PT.lead, palette.dark, { bold: true }));
  if (cues.length) addText(slide, "cues", cues.map((x) => `• ${x}`).join("\n"), { left: 160, top: 390, width: 960, height: 190 }, textStyle(PT.body, palette.ink));
}

export function explanationSlide(slide, { title, points, palette, number }) {
  slide.background.fill = palette.paper;
  addHeader(slide, title, palette, number);
  addText(slide, "explanation", points.map((x) => `• ${x}`).join("\n"), { left: 92, top: 142, width: 1080, height: 470 }, textStyle(PT.body, palette.ink));
}

export function sourceAnalysisSlide(slide, { title, excerpt, questions, palette, number }) {
  slide.background.fill = palette.paper;
  addHeader(slide, title, palette, number);
  addText(slide, "source-excerpt", excerpt, { left: 72, top: 132, width: 570, height: 460 }, textStyle(20, palette.ink));
  addText(slide, "source-questions", questions.map((x, i) => `${i + 1}. ${x}`).join("\n"), { left: 690, top: 132, width: 490, height: 460 }, textStyle(PT.body, palette.dark));
}

export function workedExampleSlide(slide, { title, steps, result, palette, number }) {
  slide.background.fill = palette.paper;
  addHeader(slide, title, palette, number);
  addText(slide, "example-steps", steps.map((x, i) => `${i + 1}. ${x}`).join("\n"), { left: 82, top: 136, width: 760, height: 450 }, textStyle(PT.body, palette.ink));
  addText(slide, "example-result", result, { left: 890, top: 230, width: 290, height: 170 }, textStyle(PT.lead, palette.dark, { bold: true }));
}

export function taskSlide(slide, { title, instruction, steps, success, palette, number }) {
  slide.background.fill = palette.paper;
  addHeader(slide, title, palette, number);
  addText(slide, "task-instruction", instruction, { left: 76, top: 124, width: 1090, height: 90 }, textStyle(PT.lead, palette.dark, { bold: true }));
  addText(slide, "task-steps", steps.map((x, i) => `${i + 1}. ${x}`).join("\n"), { left: 92, top: 246, width: 700, height: 330 }, textStyle(PT.body, palette.ink));
  addText(slide, "task-success", `Критерий успеха\n${success}`, { left: 850, top: 270, width: 330, height: 220 }, textStyle(PT.subhead, palette.dark, { bold: true }));
}

export function assessmentSlide(slide, { title, questions, palette, number }) {
  slide.background.fill = palette.paper;
  addHeader(slide, title, palette, number);
  addText(slide, "assessment", questions.map((x, i) => `${i + 1}. ${x}`).join("\n"), { left: 110, top: 160, width: 1040, height: 410 }, textStyle(PT.body, palette.ink));
}

export function reflectionSlide(slide, { title, prompts, palette, number }) {
  slide.background.fill = palette.paper;
  addHeader(slide, title, palette, number);
  addText(slide, "reflection", prompts.map((x) => `• ${x}`).join("\n"), { left: 126, top: 172, width: 1010, height: 380 }, textStyle(PT.lead, palette.dark));
}

export function homeworkSlide(slide, { title, homework, sources = [], palette, number }) {
  slide.background.fill = palette.paper;
  addHeader(slide, title, palette, number);
  addText(slide, "homework", homework, { left: 90, top: 150, width: 1080, height: 260 }, textStyle(PT.lead, palette.dark, { bold: true }));
  if (sources.length) addText(slide, "visible-sources", `Источники: ${sources.join("; ")}`, { left: 90, top: 540, width: 1080, height: 70 }, textStyle(PT.source, palette.ink));
}

export const SCHOOL_LAYOUTS = Object.freeze({
  title: titleSlide,
  objectives: objectivesSlide,
  prompt: promptSlide,
  explanation: explanationSlide,
  sourceAnalysis: sourceAnalysisSlide,
  workedExample: workedExampleSlide,
  task: taskSlide,
  assessment: assessmentSlide,
  reflection: reflectionSlide,
  homework: homeworkSlide,
});
