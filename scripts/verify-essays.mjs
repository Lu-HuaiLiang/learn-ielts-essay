import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {groupEssays, loadEssays, root, validateEssays, validateTranslations} from './essay-library.mjs';

const essays = await loadEssays();
const analyses = JSON.parse(await readFile(path.join(root, 'data/essay-analysis.json'), 'utf8'));
assert.equal(Object.keys(analyses).length, 70);
validateEssays(essays);
validateTranslations(essays, JSON.parse(await readFile(path.join(root, 'data/essay-translations.json'), 'utf8')));
const context = {};
vm.runInNewContext(await readFile(path.join(root, 'course-data.js'), 'utf8'), context);
const legacy = JSON.parse(JSON.stringify(context.COURSES));
const originals = (await Promise.all(['eight', 'nine', 'five'].map(async group =>
  JSON.parse(await readFile(path.join(root, `data/${group}.json`), 'utf8'))
))).flat();

function signature(markdown) {
  let bold = false;
  const result = [];
  for (const part of markdown.split(/(\*\*)/)) {
    if (part === '**') bold = !bold;
    else for (const character of part) if (!/\s/u.test(character)) result.push([character, bold]);
  }
  assert.equal(bold, false, 'Unbalanced emphasis');
  return result;
}

assert.equal(essays.length, 70);
assert.deepEqual(essays.map(essay => essay.id), legacy.map(essay => essay.id));
for (const [i, essay] of essays.entries()) {
  const old = legacy[i];
  const original = originals.find(record => record.sourceGroup === old.sourceGroup && record.code === old.code);
  assert.equal(essay.question, old.question, `${essay.id}: prompt changed`);
  assert.deepEqual(essay.paragraphs, original.essayParagraphs, `${essay.id}: paragraph changed`);
  assert.deepEqual(analyses[essay.id]?.paragraphNotes, original.paragraphNotes, `${essay.id}: original paragraph analysis changed`);
  assert.deepEqual(analyses[essay.id]?.corrections, original.corrections, `${essay.id}: original revision analysis changed`);
  assert.equal(essay.paragraphs.length, old.essay.length);
  essay.paragraphs.forEach((paragraph, index) => {
    assert.deepEqual(signature(paragraph), signature(old.essay[index].join(' ')), `${essay.id}: text or bold changed`);
  });
  for (const field of ['teaching', 'steps', 'collocations', 'answers', 'questions', 'transfer', 'position', 'sourceCorrections']) {
    assert(!Object.hasOwn(essay, field), `${essay.id}: unexpected teaching field ${field}`);
  }
}
const {topics, types} = groupEssays(essays);
assert.equal(topics.length, 22);
assert.deepEqual(types.map(type => type.essays.length), [33, 20, 6, 3, 3, 5]);
for (const groups of [topics, types]) {
  const ids = groups.flatMap(group => group.essays.map(essay => essay.id));
  assert.equal(ids.length, 70);
  assert.equal(new Set(ids).size, 70);
}
console.log('PASS: 70 original prompts, all paragraphs, bold characters and original analyses preserved; complete sentence-aligned Chinese translations; 22 topics and 6 question types cover every essay.');
