# Mandatory Teacher Interview Gate

## Purpose

Prevent fabricated teacher, class, curriculum, and lesson data. Apply this gate before every new KSP, including demonstrations and requests for a realistic example.

## Required confirmed data

Obtain from the teacher's messages or attached documents and confirm in the current conversation:

- subject;
- grade;
- language of instruction;
- curriculum section;
- lesson topic for each requested lesson;
- exact learning-objective codes and official wording for each requested lesson;
- number of lessons to plan;
- class size;
- teacher experience;
- attestation level or qualification category;
- class characteristics that affect learning or lesson organization.

For chemistry, biology, physics, natural science, and arts/crafts (`Көркем еңбек`), also obtain and confirm the class's practical-work capacity. Ask on the user's language:

> Сыныпта практикалық немесе зертханалық жұмысты өткізуге қандай мүмкіндік бар? Қолжетімді кабинет, құрал-жабдықтар, материалдар, реактивтер, қауіпсіздік құралдары, цифрлық құрылғылар және жұмыс форматын көрсетіңіз. Мүмкіндік шектеулі болса, нақты нені қолдануға болмайтынын жазыңыз.

Accept a concise answer such as `толық мүмкіндік бар`, `ішінара мүмкіндік бар`, or `практикалық мүмкіндік жоқ`, but record the concrete available and unavailable resources whenever supplied. If the teacher answers that capacity is partial without naming the limitation, ask one conditional follow-up: `Қандай құралдар немесе материалдар қолжетімді, ал қайсысын қолдануға болмайды?` Do not ask this practical-capacity question for other subjects unless the planned activity itself requires special equipment or materials.

Never infer, generate, complete, or silently normalize these values. Preserve supplied learning objectives verbatim. If a probable error is present, quote it and ask for confirmation.

Use the fixed rule `1 lesson = 40 minutes`. Never ask the teacher for lesson duration, offer duration choices, or mark minutes as missing. Ask the mandatory question «На сколько уроков создать поурочный план?» (or its Kazakh/English equivalent) only when the number is not already known. Require a positive whole number. For more than one lesson, require a confirmed topic and exact learning objectives for every lesson, whether supplied directly or found in an attached teacher document.

Before treating `curriculum section` as missing, inspect annual KTP files uploaded by the teacher in the current Project. Match the lesson by subject and grade, then by topic, lesson sequence, or exact learning objective. When one row matches unambiguously, copy the section title verbatim from that KTP, record the filename as its source, include it in the confirmation summary, and do not ask the teacher for the section separately. If several rows or files remain plausible, show only the candidate section titles with their sources and ask the teacher to choose. Never resolve an ambiguity by guessing.

## Interaction protocol

1. Extract every required value already supplied in the current conversation or attached source, checking an uploaded annual KTP for the curriculum section before marking it missing.
2. Present a compact summary with `получено` and `не получено` states.
3. Ask all missing mandatory questions in one grouped message, including the practical-capacity question when the subject is chemistry, biology, physics, natural science, or arts/crafts.
4. Ask the teacher to confirm or correct the complete summary.
5. End the response and wait.
6. Continue only after the teacher explicitly confirms the complete data set.

Do not proceed on the basis of assumptions, common school practice, an earlier synthetic example, script fixtures, or values from another class. Do not treat the user's request for speed as confirmation.

If the teacher refuses or cannot provide one or more required values, state that a new KSP and DOCX cannot yet be created and identify only the missing values. Do not offer a fabricated draft as a workaround.

## Demonstration mode

For requests such as «покажи работу навыка», «создай демонстрацию» or «придумай реалистичный пример»:

1. Show a short example of what a teacher could ask, using visible placeholders rather than completed professional or lesson data.
2. In a separate message, begin the real interview and ask for the user's own data.
3. Stop and wait for the user's answer.
4. Do not answer the interview questions on the user's behalf.
5. Do not create lesson content or DOCX until the complete data set is confirmed.

Technical fixtures printed by scripts are for developer validation only. Never present them as teacher responses or as a completed demonstration.

## Pre-generation record

Before generating a bundled-form DOCX, create an internal intake record containing:

- `confirmed_by_user: true`;
- the eleven general confirmed field names, including `lesson_count` instead of lesson duration;
- `practical_resources` as an additional confirmed field for chemistry, biology, physics, natural science, and arts/crafts;
- a concise source summary identifying teacher messages or attached documents;
- no inferred or synthetic values.

Pass this record to the DOCX builder. If it is incomplete, stop generation.
