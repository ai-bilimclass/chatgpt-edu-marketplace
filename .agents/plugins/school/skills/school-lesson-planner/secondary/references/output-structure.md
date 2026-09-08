# Output and DOCX Structure

## Contents

- Chat output before document generation
- KSP section based on the Kazakhstan form
- User-supplied template fidelity
- Methodological appendix
- Supporting-material packaging
- Deterministic DOCX generation
- DOCX typography and quality

## Chat output before document generation

Provide a concise methodological note containing:
- interpretation of the learning objectives;
- selected lesson model and justification;
- central evidence of learning;
- key class-context decisions;
- any assumptions that remain.

## KSP section based on the Kazakhstan form

Use this section only when no user-supplied template is designated. Read `references/normative-basis.md`, select the template matching the document language, and preserve its structure:

- Kazakh -> `assets/ksp-template-kk.docx`;
- Russian -> `assets/ksp-template-ru.docx`;
- English -> `assets/ksp-template-en.docx` (working translation; not an official language version of the order).

- organization name;
- title: Short-term (lesson) plan;
- lesson topic;
- section;
- teacher name;
- date;
- grade;
- present/absent counts;
- learning objectives according to the curriculum;
- lesson objectives;
- assessment criteria (`Бағалау критерийлері` / `Критерии оценивания` / `Assessment criteria` according to the document language);
- lesson progress table with columns in the order used by the source form:
  - stage/time;
  - teacher actions;
  - learner actions;
  - assessment.
  - resources;

Use blank placeholders for administrative fields not provided. Never invent teacher name, date, organization, or attendance.

Always render `lesson objectives` and `assessment criteria` as true bulleted lists in their table cells: one objective or criterion per bullet. In JSON, both fields must be arrays with one clean item per array element. Do not place several items in one string, use embedded line breaks, or type bullet/number symbols manually. The builder must reject those inputs and verify the resulting Word bullet count.

For every task in the lesson progress table, include a separate observable localized descriptor in the assessment cell. In every applicable `teacher_actions` cell, put the method or technique on its own list item using triple emphasis markers: `***Әдіс-тәсіл: …***`, `***Метод/приём: …***`, or `***Method/technique: …***`. The DOCX builder removes the markers and renders that line bold italic; the remaining teacher actions stay in regular type.

The assessment-criteria row is a methodological addition to the mandatory minimum of the bundled form, not a separate mandatory field of Order No. 130. Do not add a separate or combined expected-results field (`Күтілетін нәтиже`, `Ожидаемый результат`, or `Expected result(s)`) to the bundled form. Do not label assessment criteria as success criteria.

## User-supplied template fidelity

When the teacher supplies or explicitly designates a DOCX template, it overrides all bundled forms. Work from a copied file and preserve exactly:

- every section title and label;
- section and row order;
- table count, row and column count;
- merged-cell topology;
- page orientation, margins, widths, and overall geometry;
- headers, footers, styles, numbering, and fixed instructional text.

Fill existing cells and placeholders without rebuilding the form. Keep an unmodified copy as the comparison baseline. Do not use `scripts/build_ksp.py` when it would replace or restructure the supplied template.

If the designated template is not accessible in the current conversation, request it and stop DOCX generation. Never reconstruct an allegedly exact template from a prose description.

Fill each original section or leave a clear administrative placeholder when the value is not supplied and invention is prohibited. Append the methodological appendix only after the complete original form; do not insert new rows or fields into the original tables.

Preserve template-specific fields even when they are absent from the bundled forms. This includes, when present: school, teacher name, outcomes for all/most/some learners, language objective, key words and phrases, language style, discussion questions, prompts, prior learning, beginning/middle/end stages, differentiation, assessment, cross-curricular links, sanitary and safety requirements, values, lesson summary, and extended reflection. Do not reinterpret these fields as prohibited additions.

Before delivery, render both the source template and completed copy. Compare every page for section names, order, merges, geometry, and unexpected layout shifts. Repair any mismatch before delivery.

## Methodological appendix

Append these sections after the official plan:

1. **Methodological analysis of learning objectives**
   - knowledge, skills, cognitive demand, evidence.

2. **Knowledge and skills developed through the learning objective and lesson topic**
   - subject content;
   - factual knowledge;
   - subject-specific skills;
   - cognitive skills and actual Bloom level.

   Use exactly these four localized rows, in this order. Do not add separate rows for conceptual knowledge, procedural knowledge, metacognitive knowledge, final evidence of learning, or additional skills. Express the evidence through the methodological analysis of the objective and assessment criteria. Use the labels defined in `../../references/methodological-appendix.md`.

3. **Application of the selected methodology**
   - pedagogical function;
   - selected method-card mechanism;
   - lesson stage and learner action;
   - evidence collected;
   - teacher adjustment when understanding is insufficient.

4. **Use of previous-lesson reflection**
   - what is retained;
   - what is corrected;
   - which gap is addressed;
   - which groups receive support or extension.

5. **Rationale for lesson model**

**Immediate term explanation rule.** When a specialized method name, acronym, or professional term first appears in any appendix section, place the localized **Brief explanation of terms** block immediately after that section:
   - full name or expansion;
   - plain-language meaning;
   - its function in this lesson;
   - methodological-recommendation status for a pedagogical model or technique.

Do not postpone the explanation until the end of the appendix. Do not create this section when no specialized term is used. Do not use a definition as a substitute for showing the method's mechanism in the lesson.

6. **Differentiation and inclusive design**
   - universal supports;
   - targeted scaffolds;
   - extension;
   - alternative participation/output formats.

7. **Formative-assessment logic**
   - evidence collected;
   - timing;
   - feedback;
   - teacher adjustment if learning is insufficient.

8. **Alternative and reserve tasks**

9. **Sources**; always order the three entries as learning objectives, applied teaching methodology, and the lesson-plan form based on the plugin reference for Order No. 130

10. **Professional notice** — use the fixed localized notice from the builder. Do not show the internal-audit summary in the teacher-facing DOCX. The audit remains an internal pre-delivery gate.

## Supporting-material packaging

Place short materials in the same document. Create separate files when worksheets, task-card sets, SEN materials, or rubrics are substantial or intended for separate printing.

## Deterministic DOCX generation

Create a UTF-8 JSON input and run:

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" scripts/build_ksp.py input.json output.docx
```

Run from the skill directory or use an absolute path to the script. Use `--print-example` to print a schema fixture that still requires real teacher confirmation, and `--check output.docx` to run structural checks on an existing result.

The JSON must contain:

- `intake_verification` confirming the real teacher interview;
- `language`: `kk`, `ru`, or `en`;
- `lesson_count`: the positive whole number confirmed by the teacher;
- `subject`, `grade`, `section`, `topic`;
- `class_size`, `teacher_experience`, `qualification_category`, and `class_characteristics`;
- `practical_resources` for chemistry, biology, physics, natural science, and arts/crafts, confirmed from the teacher's description of available and unavailable facilities, equipment, materials, safety resources, devices, and work formats;
- exact `learning_objectives` from the teacher or source document;
- derived `lesson_objectives`;
- `assessment_criteria`;
- one or more `stages`, each with `name`, `minutes`, `teacher_actions`, `learner_actions`, `assessment`, and `resources`;
- every task represented in a stage must have its own observable descriptor in `assessment`; method/technique items in `teacher_actions` must use the triple-emphasis form so they become bold italic in DOCX;
- `methodological_appendix` with `goal_analysis`, `knowledge_skills_analysis`, `methodology_application`, `model_rationale`, `differentiation`, `formative_assessment`, `alternatives`, and `audit_summary`; add `term_explanations` when a specialized method name or acronym is used.

Administrative fields `organization`, `teacher`, `date`, `present`, and `absent` may be empty. Do not invent them. `reflection_use`, `term_explanations`, and `external_resources` in the appendix are conditional; include them only when applicable.

`intake_verification` must contain `confirmed_by_user: true`, `confirmed_fields` listing all eleven mandatory field names, including `lesson_count`, and a non-empty `source_summary` identifying the teacher messages or attached documents used. Script fixtures are schema examples, not evidence of user confirmation.

Do not pass `lesson_duration_minutes`; duration is not a user input. The builder enforces the fixed value of 40 minutes and rejects any lesson whose stage minutes do not total 40. For several requested lessons, prepare one validated JSON input and one separate DOCX per lesson, using the same confirmed `lesson_count` and the corresponding topic and exact learning objectives.

The script must reject an incomplete or unconfirmed interview record, missing instructional fields, a non-positive lesson count, any attempt to override the fixed duration, stage minutes that do not total 40, prohibited field labels, malformed stages, non-array lesson objectives or assessment criteria, embedded line breaks or typed markers in those fields, and a missing core methodological appendix. Prohibited phrases are checked as field names or labels, not banned from legitimate explanatory prose. The script selects the language template, preserves the KSP table structure, creates one real Word bullet per item, verifies the bullet count, repeats the lesson-table header, applies Times New Roman 12 pt, appends the methodological appendix, and performs a structural audit.

After the script succeeds, render the DOCX with the canonical renderer from the `documents` skill, inspect every page PNG, fix content or layout defects, and rerun generation and rendering. Script success does not replace visual QA.

## DOCX typography and quality

- Use **Times New Roman, 12 pt** throughout the official KSP, all table cells, methodological appendix, supporting materials, footnotes, and administrative placeholders unless the user explicitly requests another format.
- Keep headings in Times New Roman; use bold for hierarchy while retaining 12 pt by default.
- Apply the font at both style and run level so text inserted into tables does not inherit another font.
- Set Latin, Cyrillic, and East Asian font mappings to Times New Roman in the DOCX XML.
- Use readable headings, stable tables, repeating header rows when tables span pages, adequate cell padding, and consistent spacing.
- Render every final DOCX to PNG and inspect all pages before delivery.
