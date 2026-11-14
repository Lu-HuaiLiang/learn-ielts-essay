# Water Essay Course Implementation Plan

> Execute inline with superpowers:executing-plans. The user explicitly requests direct implementation without further approval; desktop layout only.

**Goal:** Deliver two scrollytelling IELTS courses with corrected English on black at left and Chinese teaching on white at right.
**Architecture:** Dependency-free static page, separated course data, navigation model, DOM interactions and styles. Generate a self-contained HTML for direct opening as well as the local preview.
**Tech Stack:** HTML, CSS, browser JavaScript, Node built-in tests.
**Spec:** ../specs/2026-10-17-water-essay-course-design.md

## Global constraints
- Preserve the supplied revised English and bold edits exactly.
- Use the provided writing skill's reasoning, collocation slots, source distinctions and recall methodology.
- Desktop only; latest user direction supersedes mobile adaptation.
- Local project in the user-specified directory; no account, backend or hosting required.

## Review focus
- Switching courses must not leak step/answer state across courses.
- Stored progress may be corrupt, out of bounds, or unavailable; reading must still work.
- Scrolling upward, jumping through the outline, and clicking English must agree on the current step.
- Long active sentences must remain visible inside the fixed English panel.
- Recall solutions must remain hidden until actively revealed.

### Task 1 Course data and progress model
Files: course-data.js, course-model.js, tests/model.test.mjs.
Interfaces: COURSES contains paragraphs of sentences, steps referencing sentence IDs, collocations and recall; CourseModel exports restoreProgress, selectStepAtLine, stepForSentence, wordCount.
- [x] Add meaningful tests for malformed progress, bounds, multi-course memory, viewport selection and English sentence routing; watch fail.
- [x] Implement normalization, progress resolution, viewport selection and sentence routing.
- [x] Import teaching from the reviewed manuscript, transcribe revised essays, verify word counts and references.
- [x] Run node --test.

### Task 2 Desktop reading experience
Files: index.html, style.css, app.js.
Interfaces: app consumes COURSES and CourseModel; renders sentence IDs and step IDs as stable anchors.
- [x] Render fixed black English panel, scrolling white teaching panel, course tabs, outline, progress and step controls.
- [x] Add synchronized scroll, sentence links, course-specific resume, modified-text emphasis, outline keyboard access and collapsed recall answers.
- [x] Preview using a local static server, verify desktop scroll and both course switches in a real browser.

### Task 3 Delivery and verification
Files: scripts/build.mjs, package.json, README.md, dist/index.html.
- [x] Generate dependency-free standalone HTML; copy deliverable to the chat outputs directory.
- [x] Verify data anchors, English totals, syntax, navigation, storage failures and recall answers.
- [x] Inspect desktop screenshots and correct observed issues.
- [x] Package source and document how to run locally.

## Execution ledger

Ruling: Work directly in the requested new directory; it is not inside a Git repository, so a Git worktree or commit would create an unrelated repository.
Ruling: User's direct-execution instruction waives skill review pauses; proceed inline.
Ruling: Deliver local files and a local preview, consistent with the approved specification and requested directory.

Task 1: complete — npm test passes 7 model contracts; word counts 292 / 341, all 31 sentence anchors covered.
Task 2: complete — real browser verified outline jumps, sentence clicks, reverse scrolling, independent course resume, opt-in answers, keyboard activation and refresh resume.
Task 3: complete — standalone 72 KB HTML built, desktop screenshot saved, source packaged.
Ruling: automated browser script first exposed a test-positioning issue; corrected its scrolling and selectors. Runtime acceptance was completed through cua_repl; only the 7 model tests are reported as automated passes.
Final review: independent reviewer found no Critical or Important issues. Subsequent reading-position correction was reproduced in the browser, covered by a failing-then-passing regression test, and rechecked across reloads.
