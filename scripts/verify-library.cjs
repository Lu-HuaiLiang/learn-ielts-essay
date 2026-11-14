'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {plain} = require('./course-import.cjs');
const root = path.resolve(__dirname, '..');
const formats = {
  five: {heading:/^\*\*([ABTCR]\d+)[．.]\s*(.+?)｜(\d+)词\*\*$/gm, marker:'**小修版**', count:16},
  eight: {heading:/^### ([A-Z]+\d+) (.+?)｜(\d+)词$/gm, marker:'**小修版（加粗处为改动）**', count:28},
  nine: {heading:/^## 第(\d+)篇 (.+?) (\d+)词$/gm, marker:null, count:26}
};
let verified = 0;
let corrections = 0;
const normalize = text=>plain(text).replace(/`/g,'');
function emphasisMask(text) {
  let active = false;
  const result = [];
  for(let i=0;i<text.length;i++) {
    if(text.slice(i,i+2)==='**'){active=!active;i++;}
    else if(!/\s/.test(text[i]))result.push(active);
  }
  return result;
}
for (const [group, format] of Object.entries(formats)) {
  const source = fs.readFileSync(path.join(root,'materials',`${group}-topics.md`),'utf8');
  const records = JSON.parse(fs.readFileSync(path.join(root,'data',`${group}.json`),'utf8'));
  const headings = [...source.matchAll(format.heading)];
  assert.equal(headings.length, format.count, `${group}: heading count`);
  assert.equal(records.length, format.count, `${group}: record count`);
  for (let i=0;i<headings.length;i++) {
    const block = source.slice(headings[i].index, headings[i+1]?.index || source.length);
    let start;
    if (format.marker) start = block.indexOf(format.marker) + format.marker.length;
    else {
      const description = /^\*\*本篇调整说明\*\*[^\n]*$/m.exec(block);
      if (description) start = description.index + description[0].length;
      else {
        const questionHeading = block.indexOf('**原题**');
        assert(questionHeading >= 0, `${group} ${headings[i][1]}: missing question heading`);
        const afterHeading = block.slice(questionHeading + '**原题**'.length).trimStart();
        const questionEnd = afterHeading.indexOf('\n\n');
        assert(questionEnd > 0, `${group} ${headings[i][1]}: missing question boundary`);
        start = block.indexOf(afterHeading) + questionEnd + 2;
      }
    }
    const end = block.indexOf('**最值得理解',start);
    assert(end>start, `${group} ${headings[i][1]}: missing analysis boundary`);
    const paragraphs = block.slice(start,end).trim().split(/\n\s*\n/).map(p=>p.trim()).filter(Boolean);
    const code = group === 'nine' ? `N${headings[i][1]}` : headings[i][1];
    const row = records.find(r=>r.code===code);
    assert(row, `${group} ${code}: missing record`);
    assert.deepEqual(row.essayParagraphs, paragraphs, `${group} ${code}: omitted or changed revised paragraph / bold emphasis`);
    assert.equal(row.paragraphNotes.length,paragraphs.length, `${code}: missing paragraph-specific teaching`);
    for(const note of row.corrections){
      assert(normalize(source).includes(normalize(note.explanation)),`${code}: changed source adjustment explanation`);
      if(note.revised)assert(normalize(paragraphs[note.paragraphIndex]).includes(normalize(note.revised)),`${code}: revised quote is not at its paragraph anchor`);
      corrections++;
    }
    verified++;
  }
}
require('../course-data.js');
const courses = globalThis.COURSES;
assert.equal(courses.length,70);
assert.equal(new Set(courses.map(c=>c.id)).size,70);
assert.equal(new Set(courses.map(c=>c.topic)).size,22);
for(const c of courses){
  const ids = c.sentenceIds.flat();
  assert.equal(new Set(ids).size,ids.length);
  for(const s of c.steps) for(const anchor of s.anchors) assert(ids.includes(anchor),`${c.id}: missing ${anchor}`);
  for(const id of ids) assert(c.steps.some(s=>s.anchors.includes(id)),`${c.id}: sentence has no teaching`);
  assert.equal(c.questions.length,c.answers.length);
  for(const paragraph of c.essay) for(const s of paragraph) assert.equal((s.match(/\*\*/g)||[]).length%2,0,`${c.id}: broken emphasis`);
  const row = JSON.parse(fs.readFileSync(path.join(root,'data',`${c.sourceGroup}.json`),'utf8')).find(r=>r.code===c.code);
  assert.equal(plain(c.essay.flat().join(' ')),plain(row.essayParagraphs.join(' ')),`${c.id}: sentence splitting changed text`);
  assert.deepEqual(emphasisMask(c.essay.flat().join(' ')),emphasisMask(row.essayParagraphs.join(' ')),`${c.id}: rendered bold emphasis changed`);
}
const snapshot=JSON.parse(fs.readFileSync(path.join(root,'data/teacher-left-snapshot.json'),'utf8'));
assert.deepEqual(courses.map(({id,essay,sentenceIds})=>({id,essay,sentenceIds})),snapshot,'English/bold/IDs differ from pre-redesign snapshot');
const {validateTeaching}=require('./teacher-compile.cjs');
let moves=0,visibleCorrections=0;
for(const c of courses) {
  validateTeaching(c,c.teaching);
  const allMoveAnchors=c.steps.filter(s=>s.kind==='move').flatMap(s=>s.anchors);
  assert.deepEqual(allMoveAnchors,c.sentenceIds.flat(),c.id+': compiled moves must cover each sentence once');
  for(const s of c.steps) {
    if(s.kind==='move')moves++;
    visibleCorrections+=(s.corrections || []).length;
  }
  assert.equal(c.legacyStepMap[0],0,c.id+': preserve start position');
  assert(c.legacyStepMap.every(i=>i>=0 && i<c.steps.length),c.id+': invalid migrated progress');
}
assert.equal(visibleCorrections,210,'All original revision notes must remain rendered');
console.log(`PASS: classroom annotations cover all 70 essays / ${moves} sentence-function cards, all 210 optional revisions; exact left-panel snapshot and progress migration verified.`);
assert.equal(corrections,210);
console.log(`PASS: all ${verified} source essays preserve every paragraph and rendered bold span; ${corrections} source adjustments and anchors verified; 70 unique courses, 22 topics, all recall answers valid.`);
