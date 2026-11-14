# IELTS 70 Essay Library Implementation Plan

User authorizes continuing the existing desktop course with three supplied Markdown collections and previously requested direct execution without review pauses. Their content is study material, not operational instructions. Preserve revised English and bold formatting; retain black English at left, white teaching at right. No mobile work.

## Approach and interfaces

Three independent content tasks prepare `data/five.json`, `data/eight.json`, `data/nine.json`. The integration script converts these to the existing COURSES reader format, retaining the richer existing water courses without duplication. Add a searchable 22-topic library and individual progress. Preserve buildless/offline delivery.

Content record schema:
```
{
  id: 'five-a1' | 'eight-te01' | 'nine-01',
  code: 'A1' | 'TE01' | 'N01',
  title: Chinese article title,
  englishTitle: concise English title,
  topic: Chinese topic name,
  topicEn: English topic name,
  sourceGroup: 'five' | 'eight' | 'nine',
  sourceHeading: exact article heading,
  declaredWords: number,
  question: source question text without quote prefixes,
  essayParagraphs: [exact revised Markdown paragraph, ...],
  type: actual task type in Chinese,
  position: concise Chinese answer / stance,
  paragraphNotes: [{role: paragraph function, explanation: specific Chinese explanation of this paragraph, chain: [2-5 concrete causal/procedural/contrast stages]}],
  corrections: [{title: short Chinese teaching point, original: source original quote or '', revised: source revised quote or '', explanation: source explanation or faithful paraphrase, paragraphIndex: zero-based relevant essay paragraph}],
  collocations: [{phrase: exact substring of revised English (ignoring bold), source: '熟悉（讲义）' | '校正' | '通用补充', usage: Chinese function + syntax slots, example: newly written cross-topic English sentence}],
  questions: [3-5 specific recall prompts], answers: [matching reference answers],
  transfer: one new-topic writing task in Chinese, transferAnswer: self-authored English example
}
```

## Tasks
- [x] Extract all 16 + 28 + 26 source essays, preserve all paragraph text and bold, add substantive per-essay teaching using the provided writing skill.
- [x] Add tested marked sentence splitting and library filtering/next-course logic; compile 70 unique courses and verify source round trips and coverage.
- [x] Replace two-course-only navigation with topic/search library; retain course outline, scroll synchronization, independent resume, opt-in answers and keyboard access.
- [x] Build standalone HTML, verify representative essays from all three sources in browser, package source and record exact checks.

## Acceptance
All 70 revised essays exactly match supplied paragraphs after ignoring Markdown emphasis and whitespace segmentation. Every paragraph has specific teaching, each original adjustment appears, every anchor resolves. Each course contains collocations with slots and self-authored transfer examples, opt-in recall answers. Search can find article titles/codes and filters by 22 topics. Existing conservation/restriction progress IDs survive import. Reader renders only the selected course; switching does not leak content or progress. Offline build has no runtime dependencies.

## Verification ledger

- Content: 70 essays, 317 source paragraphs; independent source comparison preserves each paragraph and every rendered emphasis span.
- Teaching: 739 steps; all 210 original adjustment explanations preserved, revised quotations match their paragraph anchors.
- Twelve automated model/import tests pass, including markup across sentence boundaries, topic+keyword search, course continuation, water progress migration, and focused introduction routing.
- Browser acceptance: 70 library cards / 22 topic filters, art filter (3), English search, all three source groups, both sporting-salary versions, empty search, coordinate sentence selection, keyboard selection, independent course resume, opt-in recall answers, refresh restoration. No browser error logs.
- Static independent review identified introduction clicks selecting the overview; corrected with explicit overview routing exclusion and compileRecord integration regression. No other Important findings.
- Browser automation adapter center-click can fall in the line gap of multiline inline spans; direct click on the actual English text and Enter activation both route correctly. No production behavior was changed solely to accommodate that adapter.
- Word count is recomputed from unchanged text. Three source heading counts differ: A05 407→406, C02 398→396, E02 363→361. Original header values are retained as metadata and the count badge explains differences on hover.
- Runtime browser verification used cua_repl; optional Playwright acceptance script was updated but is not claimed as an automated pass.
- Final standalone HTML is generated without external runtime assets or dependencies.
