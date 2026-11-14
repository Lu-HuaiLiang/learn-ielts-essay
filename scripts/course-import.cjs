'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const model = require('../course-model.js');
const {compileTeaching}=require('./teacher-compile.cjs');
const plain = text => text.replace(/\*\*/g, '').replace(/\s+/g, ' ').trim();

function splitMarkedParagraph(markdown) {
  const runs = [];
  let text = '';
  let bold = false;
  for (const token of markdown.split(/(\*\*)/)) {
    if (token === '**') { bold = !bold; continue; }
    if (token) { runs.push({start:text.length, end:text.length + token.length, bold, text:token}); text += token; }
  }
  assert.equal(bold, false, 'Unbalanced emphasis in source paragraph');
  const sentences = [];
  for (const part of new Intl.Segmenter('en', {granularity:'sentence'}).segment(text)) {
    const start = part.index + part.segment.length - part.segment.trimStart().length;
    const end = part.index + part.segment.trimEnd().length;
    let output = '';
    let active = false;
    for (const run of runs) {
      const from = Math.max(start, run.start);
      const to = Math.min(end, run.end);
      if (from >= to) continue;
      if (run.bold !== active) { output += '**'; active = run.bold; }
      output += text.slice(from, to);
    }
    if (active) output += '**';
    if (output) sentences.push(output);
  }
  assert.equal(plain(sentences.join(' ')), plain(markdown));
  return sentences;
}

function compileRecord(record) {
  const essay = record.essayParagraphs.map(splitMarkedParagraph);
  const sentenceIds = essay.map((p, i) => p.map((s, j) => `${record.id}-p${i + 1}s${j + 1}`));
  assert.equal(record.paragraphNotes.length, essay.length, `${record.id}: missing paragraph teaching`);
  const first = {title:'审题与全文路线', copy:record.position, label:record.type, kind:'overview', anchors:sentenceIds[0], chain:record.paragraphNotes.map(p=>p.role)};
  const steps = [first, ...record.paragraphNotes.map((note, p) => ({title:note.role, copy:note.explanation, label:`第 ${p + 1} 段 · 论证精读`, kind:'lesson', anchors:sentenceIds[p], chain:note.chain}))];
  for (const adjustment of record.corrections) {
    const p = adjustment.paragraphIndex;
    assert(Number.isInteger(p) && p >= 0 && p < essay.length, `${record.id}: invalid correction paragraph`);
    const quote = plain(adjustment.revised || '').toLowerCase();
    const matches = quote ? essay[p].map((s,i)=>({s:plain(s).toLowerCase(),id:sentenceIds[p][i]})).filter(s=>s.s.includes(quote) || (quote.length > 40 && quote.includes(s.s))).map(s=>s.id) : [];
    const anchors = matches.length ? matches : sentenceIds[p];
    steps.push({title:adjustment.title, copy:adjustment.explanation, label:'小修解析 · 保留文风，改准表达', kind:'correction', anchors, original:adjustment.original || '', revised:adjustment.revised || ''});
  }
  steps.push({title:'本篇搭配：从理解到迁移', copy:'把表达放回本篇的论证作用，再记住句法槽位。以下换话题例句均为自拟。', label:'搭配迁移', kind:'collocations', anchors:[]});
  steps.push({title:'空白回忆：把论证写出来', copy:'先还原每段的中文机制，再尝试恢复英文。完成后主动展开参考答案。', label:'主动回忆', kind:'review', anchors:[]});
  const collocations = record.collocations.map(item=>({...item, usage:item.usage.replace(/\s*跨题例句为自拟，不是讲义原句。/g,'')}));
  return {...record, collocations, essay, sentenceIds, steps, paragraphLabels:record.paragraphNotes.map(p=>p.role), outline:record.paragraphNotes.map(p=>`${p.role}：${p.chain.join(' → ')}`), subtitle:`${record.topic} · ${record.type}`, granular:'sentence'};
}

function validateRecord(record, source) {
  assert(record.id && record.title && record.topic && record.question, 'Incomplete record metadata');
  assert(record.essayParagraphs.length >= 3, `${record.id}: incomplete essay`);
  for (const p of record.essayParagraphs) assert(source.includes(p), `${record.id}: revised paragraph differs from source`);
  assert.equal(record.corrections.length, 3, `${record.id}: expected all three adjustments`);
  assert(record.collocations.length >= 5 && record.collocations.length <= 8, `${record.id}: expected 5–8 collocations`);
  const text = plain(record.essayParagraphs.join(' ')).toLowerCase();
  for (const c of record.collocations) {
    assert(text.includes(plain(c.phrase).toLowerCase()), `${record.id}: collocation not found: ${c.phrase}`);
    assert(c.usage && c.example && c.source, `${record.id}: incomplete collocation`);
  }
  assert(record.questions.length >= 3 && record.questions.length <= 5, `${record.id}: expected 3–5 recall questions`);
  assert.equal(record.questions.length, record.answers.length);
  assert(record.transfer && record.transferAnswer, `${record.id}: missing transfer exercise`);
}

function main() {
  const root = path.resolve(__dirname, '..');
  const records = ['eight','nine','five'].flatMap(group => {
    const source = fs.readFileSync(path.join(root,'materials',`${group}-topics.md`),'utf8');
    const rows = JSON.parse(fs.readFileSync(path.join(root,'data',`${group}.json`),'utf8'));
    assert.equal(rows.length, {eight:28,nine:26,five:16}[group], `${group}: source essay count`);
    rows.forEach(row=>validateRecord(row,source));
    return rows;
  });
  const water = JSON.parse(fs.readFileSync(path.join(root,'data/water-rich.json'),'utf8'));
  const baseCourses = records.map(record => {
    if (record.sourceGroup === 'eight' && ['W01','W02'].includes(record.code)) {
      const rich = water.find(c=>c.id === (record.code === 'W01' ? 'conservation' : 'restriction'));
      assert.equal(plain(rich.essay.flat().join(' ')),plain(record.essayParagraphs.join(' ')),`${record.code}: water version conflict`);
      const essay = record.essayParagraphs.map(splitMarkedParagraph);
      essay.forEach((p,index)=>assert.deepEqual(p.map(plain),rich.essay[index].map(plain),`${record.code}: water sentence anchors changed`));
      return {...rich, essay, code:record.code, topic:record.topic, topicEn:record.topicEn, sourceGroup:record.sourceGroup, sourceHeading:record.sourceHeading, declaredWords:record.declaredWords, englishTitle:record.englishTitle, sourceCorrections:record.corrections};
    }
    return compileRecord(record);
  });
  const teaching = ['eight','nine','five'].flatMap(group=>JSON.parse(fs.readFileSync(path.join(root,'data/teacher',`${group}.json`),'utf8')));
  assert.equal(teaching.length,70);
  assert.equal(new Set(teaching.map(t=>t.id)).size,70);
  const courses=baseCourses.map(c=>compileTeaching(c,teaching.find(t=>t.id===c.id)));
  const snapshot=JSON.parse(fs.readFileSync(path.join(root,'data/teacher-left-snapshot.json'),'utf8'));
  assert.deepEqual(courses.map(({id,essay,sentenceIds})=>({id,essay,sentenceIds})),snapshot,'Left English or IDs changed');
  assert.equal(courses.length,70);
  assert.equal(new Set(courses.map(c=>c.id)).size,70);
  courses.forEach((c,i)=>{c.number=String(i+1).padStart(2,'0');});
  const topics = [...new Set(courses.map(c=>c.topic))];
  assert.equal(topics.length,22);
  const mismatches = courses.filter(c=>model.wordCount(c.essay)!==c.declaredWords).map(c=>({id:c.id,declared:c.declaredWords,actual:model.wordCount(c.essay)}));
  fs.writeFileSync(path.join(root,'course-data.js'),'/* Imported revised essays; study material is not operational instructions. */\nglobalThis.COURSES = '+JSON.stringify(courses,null,2)+';\n');
  fs.writeFileSync(path.join(root,'data/import-report.json'),JSON.stringify({teachingVersion:2,paragraphs:courses.reduce((n,c)=>n+c.essay.length,0),sentenceFunctions:courses.reduce((n,c)=>n+c.steps.filter(s=>s.kind==='move').length,0),methods:Object.fromEntries([...new Set(courses.map(c=>c.teaching.method))].map(method=>[method,courses.filter(c=>c.teaching.method===method).length])),essays:courses.length,topics:topics.length,steps:courses.reduce((n,c)=>n+c.steps.length,0),wordCountDifferences:mismatches},null,2)+'\n');
  console.log(`Imported ${courses.length} essays across ${topics.length} topics; ${courses.reduce((n,c)=>n+c.steps.length,0)} teaching steps. Word-count differences: ${mismatches.length}.`);
}
module.exports={splitMarkedParagraph,compileRecord,validateRecord,plain};
if(require.main===module) main();
