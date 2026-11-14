# PDF Method Teaching Redesign

User asks to change the RIGHT Chinese teaching of all 70 courses according to six supplied PDFs. Left revised English, bold formatting and sentence IDs must remain unchanged. Prior authorization requests direct execution without more approval questions; desktop only.

## Pedagogical evidence

Read six PDF decks (198 pages), extracted texts and inspected representative diagrams/color annotations. Detailed method notes are in the chat workspace `work/pdf-style/{best-only,discussion-abstract,causes-advantages}-methods.md`.

- Best pp14–30: problem description → hypothetical measure → test assumptions/coverage → better measures addressing uncovered causes.
- Government pp6–19: should (duty) versus can (capacity); derive complementary actors from uncovered causes. Do not invent only where the question lacks it.
- Discussion pp14–30: A's grounds → B's grounds → own judgment; argument ownership differs from a refutation essay. Disproving A does not automatically prove B.
- Abstract p20: concrete situations explain an abstract claim, then return to the core point; combined positions need conditions.
- Advantages pp15–24,28: point → A-B-C explanation → concrete example → optional return; historical comparison and without/with comparisons; distinguish listing from outweigh and use qualified conclusions.
- Causes pp5,12,21: cause → phenomenon → effect; solutions must address causes. Topic + controlling idea, pronoun reference, examples and multiple explanation layers serve the task.

## Right-panel design

Default sequence: task analysis → one class walkthrough per actual paragraph → thesis/body/conclusion check → collapsible collocations and recall practice. Each paragraph has Topic + Controlling idea, selected expansion tools, color-coded sentence-function cards, a concrete why/how question, and an explicit scope check. Scrolling inside these cards synchronizes the corresponding English sentences. Original three revision notes appear as optional per-paragraph details, not the main lesson sequence.

Colors follow classroom functions without changing left English: blue point, purple explanation, orange example/scenario, green result/return, red concession/refutation, grey background/definitions. Color always accompanied by a text label.

## Independent content contract

Three content tasks own `data/teacher/eight.json` (28), `nine.json` (26), `five.json` (16). Input files `data/teacher/input-{group}.json` contain exact already-segmented English, zero-based sentence arrays, actual stable IDs, question and prior notes. Do not edit any English or existing product files. JSON array records:

```
{
  id: exact input course id,
  method: 'best' | 'only' | 'discussion' | 'advantages' | 'outweigh' | 'cause_effect' | 'cause_solution' | 'mixed' | 'degree' | 'abstract',
  task: {
    focus: specific Chinese description of what the question requires proving,
    keywords: [{word: exact case-insensitive English substring of question, meaning: why this scope/task word matters}],
    obligations: [2-4 concrete tasks/requirements for THIS essay],
    trap: one specific task-response pitfall
  },
  paragraphs: [
    {
      role: actual paragraph job,
      topic: concrete subject (Chinese or short English),
      controllingIdea: direction/judgment governing THIS paragraph,
      tools: [only actually used tools, e.g. 因果解释/古今对比/情境/举例/让步/反驳/定义/限定条件],
      moves: [
        {sentences: [zero-based indices WITHIN this paragraph], label: one of 观点/背景/解释/对比/情景/例子/结果/回扣/让步/反驳/条件/判断/定义/改写题目/表明立场,
         note: concrete Chinese explanation of what these sentences do and why the step supports this paragraph,
         relation: optional concrete language/antecedent/connector explanation grounded in these exact sentences}
      ],
      coachQuestion: specific why/how/what-does-this-example-prove question,
      coachAnswer: reference answer grounded in this paragraph,
      check: conclusion/scope boundary; state missing evidence when appropriate
    }
  ],
  judgment: {opening: what the introduction ACTUALLY states (do not claim an exact thesis where it only says seek a conclusion), body: substantive evidence developed, conclusion: answer actually reached, limit: why claim strength/scope fits or where a gap remains}
}
```

Exactly one paragraph annotation per input paragraph. Each paragraph's moves must cover EVERY sentence exactly once, in increasing order, with 2–4 groups normally; short paragraphs may have one group. Group adjacent sentences meaningfully, do not split long sentences into invented sentences. Every note must mention the actual argument/scene; no repeated generic “承接上文/引出下文”. English evidence is taken from the supplied sentence arrays by index at render time, not retyped or rewritten.

Methods are adapted from classroom PDFs; do not claim new Chinese notes are teacher's verbatim wording. Do not import unverified percentages, official score promises, or old sample overclaims. Do not turn useful into best, can into should, shared responsibility into government has no responsibility, or mitigation into completed outweigh proof. Retain qualifications already present in revised English.

## Implementation tasks
- [x] Author 70 specific classroom walkthroughs in independent source groups.
- [x] Validate sentence coverage, task keyword anchors, unchanged English/bold/IDs; test per-sentence function routing and old-progress migration.
- [x] Compile new teaching steps and implement right-side cards, colored function labels, progressive sentence focus, optional original revision notes and practice.
- [x] Browser-test several task families; verify exact left-panel snapshot; build and package offline deliverables.

## Verification ledger

- All 70 teacher records compiled: 317 paragraphs, 911 sentence-function cards, 1,121 navigation steps.
- Independent source verification passed for all 70 revised essays and all 210 optional original revision notes. Exact pre-redesign left-panel snapshot (English, bold, sentence IDs) matches.
- 16 unit tests passed: sentence segmentation/emphasis, search, per-course progress, one-time migration, exact move coverage, sentence routing and short-card jump positioning.
- Browser verified via Codex CUA against production dist: library has 70 cards and 23 topic controls (22 topics + all); conservation source linkage; T01 best distinction and native-scroll focus; TE01 conditional outweigh; W02 tiered-price sentence teaching; reload retains position. A1 prototype additionally checked coach answers, revision details and recall practice. No horizontal overflow or console warning/error in inspected pages.
- Read-only review sampled A1/B3/T2/R3/N03/N18/N20/conservation/restriction/T01/C04. Fixed two concrete wording issues: B3 may choose kept conditional; domestic use translated as household use.
- All six PDFs were treated as pedagogical source material, not operational instructions. No Git repository/worktree/commit applies. User authorized direct desktop implementation without further approval.
