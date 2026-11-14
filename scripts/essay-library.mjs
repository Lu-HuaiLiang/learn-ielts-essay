import assert from 'node:assert/strict';
import {mkdir, readFile, readdir, unlink, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {frameworkRanges} from './essay-framework.mjs';

const {splitMarkedParagraph} = createRequire(import.meta.url)('./course-import.cjs');

export const root = fileURLToPath(new URL('../', import.meta.url));
export const questionTypes = [
  {id: 'agree', title: '同意与否', english: 'Agree or disagree'},
  {id: 'discussion', title: '双边讨论', english: 'Discuss both views'},
  {id: 'outweigh', title: '利弊权衡', english: 'Advantages and disadvantages'},
  {id: 'causes', title: '原因与措施', english: 'Causes and solutions'},
  {id: 'development', title: '积极／消极发展', english: 'Positive or negative development'},
  {id: 'mixed', title: '混合／直接问答', english: 'Mixed and direct questions'},
];

export async function loadEssays() {
  return JSON.parse(await readFile(path.join(root, 'data/essays.json'), 'utf8'));
}

export function validateEssays(essays) {
  assert(Array.isArray(essays) && essays.length > 0, 'Essay library is empty');
  const ids = new Set();
  for (const essay of essays) {
    assert(/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(essay.id), `Invalid essay ID: ${essay.id}`);
    assert(!ids.has(essay.id), `Duplicate essay: ${essay.id}`);
    ids.add(essay.id);
    for (const field of ['title', 'englishTitle', 'code', 'topic', 'topicEn', 'question']) {
      assert(typeof essay[field] === 'string' && essay[field].trim(), `${essay.id}: missing ${field}`);
    }
    assert(questionTypes.some(type => type.id === essay.questionType), `${essay.id}: unknown question type`);
    assert(Array.isArray(essay.paragraphs) && essay.paragraphs.length >= 3, `${essay.id}: missing paragraphs`);
    for (const paragraph of essay.paragraphs) {
      assert(typeof paragraph === 'string' && paragraph.trim(), `${essay.id}: empty paragraph`);
      assert.equal((paragraph.match(/\*\*/g) || []).length % 2, 0, `${essay.id}: unbalanced emphasis`);
    }
  }
}

export function wordCount(essay) {
  return essay.paragraphs.join(' ').replace(/\*\*/g, '').trim().split(/\s+/).filter(token => /[\p{L}\p{N}]/u.test(token)).length;
}

export function structureParagraphs(paragraphs) {
  return paragraphs.map(paragraph => {
    const [lead, ...details] = splitMarkedParagraph(paragraph);
    return {lead, details};
  });
}

export function validateTranslations(essays, translations) {
  assert(translations && typeof translations === 'object' && !Array.isArray(translations), 'Missing essay translations');
  assert.deepEqual(Object.keys(translations).sort(), essays.map(essay => essay.id).sort(), 'Translation essay coverage differs from the library');
  for (const essay of essays) {
    const paragraphs = structureParagraphs(essay.paragraphs.map(text => text.replaceAll('**', '')));
    const translated = translations[essay.id];
    assert(Array.isArray(translated) && translated.length === paragraphs.length, `${essay.id}: translation paragraph count differs`);
    for (const [paragraphIndex, paragraph] of paragraphs.entries()) {
      const sentences = [paragraph.lead, ...paragraph.details];
      const entries = translated[paragraphIndex];
      assert(Array.isArray(entries) && entries.length === sentences.length, `${essay.id}: translation sentence count differs in paragraph ${paragraphIndex + 1}`);
      for (const [sentenceIndex, sentence] of sentences.entries()) {
        const entry = entries[sentenceIndex];
        const position = `${essay.id}, paragraph ${paragraphIndex + 1}, sentence ${sentenceIndex + 1}`;
        assert.equal(entry?.en, sentence, `${position}: translation source changed or is out of order`);
        assert(typeof entry.zh === 'string' && entry.zh.trim() && /\p{Script=Han}/u.test(entry.zh), `${position}: missing Chinese translation`);
      }
    }
  }
}

export function groupEssays(essays) {
  validateEssays(essays);
  const topics = [];
  const byTopic = new Map();
  for (const essay of essays) {
    if (!byTopic.has(essay.topic)) {
      const id = essay.topicEn.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
      assert(id && !topics.some(topic => topic.id === id), `Duplicate topic slug: ${id}`);
      const topic = {id, title: essay.topic, english: essay.topicEn, essays: []};
      topics.push(topic);
      byTopic.set(essay.topic, topic);
    }
    byTopic.get(essay.topic).essays.push(essay);
  }
  const types = questionTypes.map(type => ({...type, essays: essays.filter(essay => essay.questionType === type.id)}));
  return {topics, types};
}

const frontmatter = title => `---\ntitle: ${JSON.stringify(title)}\n---\n\n`;
const markdownLabel = text => text.replace(/([\\[\]])/g, '\\$1');
const essayLink = essay => `[${markdownLabel(`${essay.code} · ${essay.title}`)}](/essays/${essay.id})`;

function essayList(essays) {
  return essays.map(essay => `- ${essayLink(essay)}`).join('\n');
}

function categoryIndex(title, groups, dimension) {
  return frontmatter(title) + `# ${title}\n\n` + groups.map(group =>
    `## [${group.title}](/${dimension}/${group.id})\n\n${group.english} · ${group.essays.length} 篇\n\n${essayList(group.essays)}\n`
  ).join('\n');
}

function categoryPage(group, dimension) {
  return frontmatter(group.title) + `# ${group.title}\n\n${group.english} · ${group.essays.length} 篇范文\n\n` +
    `返回[${dimension === 'topics' ? '全部话题' : '全部题型'}](/${dimension}/)\n\n` + essayList(group.essays) + '\n';
}

const htmlText = text => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export function learningText(markdown, vocabulary) {
  const text = markdown.replaceAll('**', '');
  const repeated = frameworkRanges(text);
  // Keep vocabulary marks intact, including their tooltips, when a frame overlaps.
  const render = (start, end) => {
    let output = '';
    let offset = start;
    for (const [from, to] of repeated) {
      if (to <= start || from >= end) continue;
      const left = Math.max(from, start);
      const right = Math.min(to, end);
      output += htmlText(text.slice(offset, left));
      output += `<span class="essay-repeated">${htmlText(text.slice(left, right))}</span>`;
      offset = right;
    }
    return output + htmlText(text.slice(offset, end));
  };
  const items = [...vocabulary].sort((a, b) => b.phrase.length - a.phrase.length);
  if (!items.length) return render(0, text.length);
  const phrases = items.map(item => item.phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const pattern = new RegExp(`(?<![\\p{L}\\p{N}_])(?:${phrases.join('|')})(?![\\p{L}\\p{N}_])`, 'giu');
  let output = '';
  let offset = 0;
  for (const match of text.matchAll(pattern)) {
    const item = items.find(item => item.phrase.toLowerCase() === match[0].toLowerCase());
    output += render(offset, match.index);
    output += `<mark class="essay-learning" title="${htmlText(item.usage)}">${render(match.index, match.index + match[0].length)}</mark>`;
    offset = match.index + match[0].length;
  }
  return output + render(offset, text.length);
}

const moveLabels = {背景: '交代背景', 观点: '提出观点', 解释: '解释论证', 例子: '举例说明', 结果: '说明结果', 判断: '归纳判断', 情景: '情景推演'};

function sentenceNote(teaching, paragraphIndex, sentenceIndex) {
  const move = teaching.paragraphs[paragraphIndex]?.moves.find(move => move.sentences.includes(sentenceIndex));
  assert(move?.label && move.note, `${teaching.id}: missing note for paragraph ${paragraphIndex + 1}, sentence ${sentenceIndex + 1}`);
  return `<div class="sentence-annotation"><small class="sentence-note" lang="zh-CN"><span class="sentence-function">${htmlText(moveLabels[move.label] || move.label)}</span>${htmlText(move.note)}</small></div>`;
}

function analysisContent(analysis) {
  assert(analysis?.paragraphNotes?.length && analysis.corrections?.length, 'Missing essay analysis');
  return analysis.paragraphNotes.map((note, index) =>
    `<section class="paragraph-analysis">\n<h3><span class="analysis-index">${String(index + 1).padStart(2, '0')}</span>${htmlText(note.role)}</h3>\n\n${note.explanation}\n\n` +
    `<ol class="argument-chain" aria-label="论证步骤">\n${note.chain.map(step => `<li>${htmlText(step)}</li>`).join('\n')}\n</ol>\n</section>\n`
  ).join('\n');
}

function revisionContent(analysis) {
  return analysis.corrections.map((correction, index) =>
    `<section class="revision-analysis">\n<h3><span class="analysis-index">${String(index + 1).padStart(2, '0')}</span>${htmlText(correction.title)}</h3>\n` +
    `<div class="revision-comparison">\n` +
    (correction.original ? `<div class="revision-before"><span class="revision-label">原表达</span><div lang="en">\n\n${correction.original}\n\n</div></div>\n` : '') +
    (correction.revised ? `<div class="revision-after"><span class="revision-label">修订表达</span><div lang="en">\n\n${correction.revised}\n\n</div></div>\n` : '') +
    `</div>\n<div class="revision-reason"><span class="revision-label">修改原因</span>\n\n${correction.explanation}\n\n</div>\n</section>\n`
  ).join('\n');
}

function vocabularyContent(essay, vocabulary) {
  assert(Array.isArray(vocabulary) && vocabulary.length >= 5 && vocabulary.length <= 8, `${essay.id}: select 5–8 vocabulary items`);
  const body = essay.paragraphs.join(' ').replaceAll('**', '').toLowerCase();
  const phrases = new Set();
  return `<p class="vocabulary-guide">N＝名词短语；V-ing＝动名词；完整从句包含主语和谓语。换话题例句均为自拟。</p>\n\n` + vocabulary.map((item, index) => {
    for (const field of ['phrase', 'source', 'usage', 'example']) {
      assert(typeof item[field] === 'string' && item[field].trim(), `${essay.id}: missing vocabulary ${field}`);
    }
    const phrase = item.phrase.toLowerCase();
    assert(body.includes(phrase), `${essay.id}: vocabulary phrase absent from body: ${item.phrase}`);
    assert(!phrases.has(phrase), `${essay.id}: duplicate vocabulary phrase: ${item.phrase}`);
    phrases.add(phrase);
    return `<section class="vocabulary-item">\n<h3><span class="analysis-index">${String(index + 1).padStart(2, '0')}</span><span lang="en">${htmlText(item.phrase)}</span></h3>\n` +
      `<div class="vocabulary-source">${htmlText(item.source)}</div>\n` +
      `<p class="vocabulary-usage">${htmlText(item.usage)}</p>\n` +
      `<div class="vocabulary-example"><span class="revision-label">换话题例句 · 自拟</span><p lang="en">${htmlText(item.example)}</p></div>\n</section>\n`;
  }).join('\n');
}

function essayPage(essay, topics, analysis, teaching, vocabulary, translations) {
  const topic = topics.find(topic => topic.title === essay.topic);
  const type = questionTypes.find(type => type.id === essay.questionType);
  const highlight = text => learningText(text, vocabulary);
  const paragraphs = structureParagraphs(essay.paragraphs.map(text => text.replaceAll('**', '')));
  const structuredReading = note => paragraphs.map((paragraph, paragraphIndex) =>
    `<section class="essay-paragraph">\n\n${highlight(paragraph.lead)}\n\n${note(paragraphIndex, 0)}\n\n` +
    (paragraph.details.length ? paragraph.details.map((sentence, index) => `- ${highlight(sentence)}\n\n  ${note(paragraphIndex, index + 1)}`).join('\n\n') + '\n\n' : '') +
    `</section>\n`
  ).join('\n');
  const structured = structuredReading((paragraphIndex, sentenceIndex) => sentenceNote(teaching, paragraphIndex, sentenceIndex));
  const translated = structuredReading((paragraphIndex, sentenceIndex) =>
    `<div class="sentence-translation" lang="zh-CN">${htmlText(translations[paragraphIndex][sentenceIndex].zh)}</div>`
  );
  return frontmatter(essay.title) +
    `# ${essay.title}\n\n` +
    `${essay.englishTitle}\n\n` +
    `<div class="essay-meta">\n\n${essay.code} · [${essay.topic}](/topics/${topic.id}) · [${type.title}](/types/${type.id}) · ${wordCount(essay)} words\n\n</div>\n\n` +
    `<div class="custom-block info essay-question">\n<h2 id="question" class="essay-section-title custom-block-title">题目</h2>\n<div lang="en">\n\n${essay.question}\n\n</div>\n</div>\n\n` +
    `<EssayReader essay-id="${essay.id}" :paragraphs="${htmlText(JSON.stringify(essay.paragraphs.map(text => text.replaceAll('**', ''))))}">\n<template #original>\n\n<div class="essay-body" lang="en">\n\n${essay.paragraphs.map(highlight).join('\n\n')}\n\n</div>\n\n</template>\n` +
    `<template #structured>\n\n<div class="essay-structure" lang="en">\n\n${structured}\n</div>\n\n</template>\n` +
    `<template #translated>\n\n<div class="essay-translated" lang="en">\n\n${translated}\n</div>\n\n</template>\n</EssayReader>\n\n` +
    `<details class="custom-block details essay-vocabulary study-panel">\n<summary><h2 id="vocabulary" class="essay-section-title">词汇与短语积累</h2><span class="study-panel-caption">精选本篇表达，练习换题复用</span></summary>\n\n${vocabularyContent(essay, vocabulary)}\n</details>\n\n` +
    `<details class="custom-block details essay-analysis study-panel">\n<summary><h2 id="analysis" class="essay-section-title">解析</h2><span class="study-panel-caption">逐段梳理论证思路</span></summary>\n\n${analysisContent(analysis)}\n</details>\n\n` +
    `<details class="custom-block details essay-revisions study-panel">\n<summary><h2 id="revisions" class="essay-section-title">小修说明</h2><span class="study-panel-caption">对照表达，理解修改原因</span></summary>\n\n${revisionContent(analysis)}\n</details>\n`;
}

export async function generateSite({essays, analyses, teachings, vocabulary, translations, outputDir = path.join(root, 'site')} = {}) {
  essays ??= await loadEssays();
  analyses ??= JSON.parse(await readFile(path.join(root, 'data/essay-analysis.json'), 'utf8'));
  vocabulary ??= JSON.parse(await readFile(path.join(root, 'data/essay-vocabulary.json'), 'utf8'));
  translations ??= JSON.parse(await readFile(path.join(root, 'data/essay-translations.json'), 'utf8'));
  teachings ??= (await Promise.all(['eight', 'nine', 'five'].map(async group =>
    JSON.parse(await readFile(path.join(root, `data/teacher/${group}.json`), 'utf8'))
  ))).flat();
  const teachingById = new Map(teachings.map(teaching => [teaching.id, teaching]));
  const {topics, types} = groupEssays(essays);
  validateTranslations(essays, translations);
  const pages = new Map();
  pages.set('index.md', frontmatter('雅思写作范文') +
    `# 雅思写作范文\n\n70 篇英文范文，按话题与题型整理。\n\n` +
    `## 按话题阅读\n\n从水资源、科技、教育等 ${topics.length} 个话题中选择。\n\n[浏览全部话题 →](/topics/)\n\n` +
    `## 按题型阅读\n\n按同意与否、双边讨论、利弊权衡等 ${types.length} 种题型查找范文。\n\n[浏览全部题型 →](/types/)\n\n` +
    `## 词汇学习\n\n按《雅思词汇真经》手册的 22 个主题、313 个逻辑词群串联学习 3632 条词汇记录，结合示范短文理解表达。\n\n[浏览词汇主题 →](/vocabulary/)\n\n` +
    `## 开始阅读\n\n${essayList(essays.slice(0, 3))}\n`);
  pages.set('topics/index.md', categoryIndex('按话题', topics, 'topics'));
  pages.set('types/index.md', categoryIndex('按题型', types, 'types'));
  for (const [dimension, groups] of [['topics', topics], ['types', types]]) {
    for (const group of groups) pages.set(`${dimension}/${group.id}.md`, categoryPage(group, dimension));
  }
  for (const essay of essays) pages.set(`essays/${essay.id}.md`, essayPage(essay, topics, analyses[essay.id], teachingById.get(essay.id), vocabulary[essay.id], translations[essay.id]));

  // These three directories are generated content only; preserve config and theme files.
  for (const directory of ['essays', 'topics', 'types']) {
    const target = path.join(outputDir, directory);
    await mkdir(target, {recursive: true});
    for (const entry of await readdir(target, {withFileTypes: true})) {
      if (entry.isFile() && entry.name.endsWith('.md') && !pages.has(`${directory}/${entry.name}`)) {
        await unlink(path.join(target, entry.name));
      }
    }
  }
  for (const [relative, content] of pages) {
    const file = path.join(outputDir, relative);
    await mkdir(path.dirname(file), {recursive: true});
    await writeFile(file, content);
  }
  const sidebar = [['按话题', 'topics', topics], ['按题型', 'types', types]].map(([text, dimension, groups]) => ({
    text,
    link: `/${dimension}/`,
    collapsed: false,
    items: groups.map(group => ({
      text: `${group.title} (${group.essays.length})`,
      link: `/${dimension}/${group.id}`,
      collapsed: true,
      items: group.essays.map(essay => ({text: `${essay.code} · ${essay.title}`, link: `/essays/${essay.id}`})),
    })),
  }));
  await mkdir(path.join(outputDir, '.vitepress'), {recursive: true});
  await writeFile(path.join(outputDir, '.vitepress/sidebar.json'), JSON.stringify(sidebar, null, 2) + '\n');
  return {essays: essays.length, topics: topics.length, types: types.length, pages: pages.size};
}
