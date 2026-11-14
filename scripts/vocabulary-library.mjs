import assert from 'node:assert/strict';
import {mkdir, readFile, readdir, unlink, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const chapterHeading = /^<a id="chapter-(\d{2})"><\/a>\n\n## 第 (\d{2}) 章｜(.+)$/gm;
const groupHeading = /^### 词群 (\d{2})\.(\d{2})｜(.+)$/gm;
const wordRow = /^\| (\d{2}-\d{3}) \| \*\*(.+?)\*\* \| (.+) \|$/gm;
const rewriteChapterLinks = text => text.replace(/\]\(#chapter-(\d{2})\)/g, '](/vocabulary/chapter-$1)');
const markdownLabel = text => text.replace(/([\\[\]])/g, '\\$1');
const frontmatter = (title, notes = false) => `---\ntitle: ${JSON.stringify(title)}\npageClass: vocabulary-page\n${notes ? '' : 'aside: false\n'}---\n\n`;
const htmlText = text => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const regexText = text => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const wordPattern = word => new RegExp(`(?<![\\p{L}])(${regexText(word)})(?![\\p{L}])`, 'giu');

export function formatVocabularyMeaning(meaning) {
  const pos = '(?:adj|adv|prep|conj|pron|num|art|int|aux|det|ord|adi|vi|vt|n|v)\\.';
  const labels = new RegExp(`(?:[；;]\\s*|\\s*)(?<![a-z])${pos}(?:\\s*/\\s*${pos})*`, 'gi');
  return meaning.replace(labels, (label, offset) =>
    `${meaning.slice(0, offset).trim() ? '；' : ''}${label.replace(/^[；;\s]+/, '')}`);
}

// The supplied Markdown is the content source, including its original definitions and exercises.
export function parseVocabulary(source) {
  source = source.replace(/\r\n/g, '\n');
  const headings = [...source.matchAll(chapterHeading)];
  assert.equal(headings.length, 22, 'Expected 22 vocabulary chapters');
  const appendixStart = source.search(/^## 附录 A｜/m);
  assert(appendixStart > headings.at(-1).index, 'Missing vocabulary appendices');
  for (const letter of ['A', 'B', 'C']) assert(source.includes(`## 附录 ${letter}｜`), `Missing appendix ${letter}`);
  const recordIds = new Set();
  const words = new Set();
  const chapters = headings.map((heading, index) => {
    const [, id, headingId, title] = heading;
    assert.equal(id, String(index + 1).padStart(2, '0'), 'Chapters must retain their original order');
    assert.equal(id, headingId, `Chapter ${id}: anchor and heading disagree`);
    const markdown = source.slice(heading.index + heading[0].indexOf('## 第'), headings[index + 1]?.index ?? appendixStart).trim();
    const counts = /\*\*(\d+) 条记录 · (\d+) 个词群\*\*/.exec(markdown);
    assert(counts, `Chapter ${id}: missing coverage counts`);
    const groupMatches = [...markdown.matchAll(groupHeading)];
    assert.equal(groupMatches.length, Number(counts[2]), `Chapter ${id}: lost vocabulary groups`);
    const groups = groupMatches.map((group, groupIndex) => {
      const [, chapterId, groupId, groupTitle] = group;
      assert.equal(chapterId, id, `Chapter ${id}: group belongs to a different chapter`);
      assert.equal(groupId, String(groupIndex + 1).padStart(2, '0'), `Chapter ${id}: missing or duplicate group`);
      const body = markdown.slice(group.index, groupMatches[groupIndex + 1]?.index);
      const rows = [...body.matchAll(wordRow)];
      assert(rows.length > 0, `Group ${id}.${groupId}: no vocabulary entries`);
      return {id: `group-${id}-${groupId}`, title: groupTitle, records: rows.length,
        words: rows.map(([, recordId, word, meaning]) => ({id: recordId, word, meaning, groupId: `group-${id}-${groupId}`}))};
    });
    const rows = [...markdown.matchAll(wordRow)];
    assert.equal(rows.length, Number(counts[1]), `Chapter ${id}: lost vocabulary entries`);
    assert.equal(groups.reduce((sum, group) => sum + group.records, 0), rows.length, `Chapter ${id}: ungrouped vocabulary entries`);
    for (const [, recordId, word] of rows) {
      assert(recordId.startsWith(`${id}-`), `Chapter ${id}: invalid record ${recordId}`);
      assert(!recordIds.has(recordId), `Duplicate record ${recordId}`);
      recordIds.add(recordId);
      words.add(word);
    }
    for (let number = 1; number <= rows.length; number++) {
      assert(recordIds.has(`${id}-${String(number).padStart(3, '0')}`), `Chapter ${id}: missing record ${number}`);
    }
    return {id, title, markdown, groups, records: rows.length};
  });
  const stats = {chapters: chapters.length, groups: chapters.reduce((sum, chapter) => sum + chapter.groups.length, 0), records: recordIds.size, distinctWords: words.size};
  assert.deepEqual(stats, {chapters: 22, groups: 313, records: 3632, distinctWords: 3592}, 'Handbook coverage has changed');
  return {overview: source.slice(0, headings[0].index).trim(), chapters, appendices: source.slice(appendixStart).trim(), stats};
}

export function compileVocabularyLearning(words, clusters) {
  const byId = new Map(words.map(word => [word.id, word]));
  const learning = new Map();
  for (const cluster of clusters) {
    assert(Array.isArray(cluster.ids) && cluster.ids.length > 0 && cluster.ids.length <= 5, 'Learning clusters must contain 1–5 words');
    assert.equal(cluster.examples?.length, 3, `Cluster ${cluster.ids}: expected three examples`);
    assert.equal(new Set(cluster.examples.map(example => example.en)).size, 3, `Cluster ${cluster.ids}: duplicate examples`);
    for (const example of cluster.examples) {
      assert(typeof example.en === 'string' && example.en.trim(), `Cluster ${cluster.ids}: missing English example`);
      assert(typeof example.zh === 'string' && /[\p{Script=Han}]/u.test(example.zh), `Cluster ${cluster.ids}: missing Chinese translation`);
    }
    assert(Array.isArray(cluster.related) && cluster.related.length >= 2, `Cluster ${cluster.ids}: missing associated words`);
    for (const related of cluster.related) {
      assert(related.word?.trim() && related.meaning?.trim() && related.relation?.trim(), `Cluster ${cluster.ids}: incomplete associated word`);
    }
    const groups = new Set();
    for (const id of cluster.ids) {
      const word = byId.get(id);
      assert(word, `Unknown learning word: ${id}`);
      assert(!learning.has(id), `Duplicate learning word: ${id}`);
      groups.add(word.groupId);
      for (const example of cluster.examples) assert(wordPattern(word.word).test(example.en), `${id} (${word.word}): example must use the headword: ${example.en}`);
      const collocation = cluster.collocations?.[id];
      assert(Array.isArray(collocation) && collocation.length === 2 && collocation.every(text => typeof text === 'string' && text.trim()), `${id}: missing bilingual collocation`);
      // A shared cluster association does not imply synonymy or a word-family link to every target.
      const related = cluster.related.map(item => cluster.ids.length > 1 && ['词形', '近义', '反义'].includes(item.relation)
        ? {...item, relation: '主题关联'} : item);
      learning.set(id, {examples: cluster.examples, collocation, related});
    }
    assert.equal(groups.size, 1, `Cluster ${cluster.ids}: use words from the same original group`);
  }
  for (const word of words) assert(learning.has(word.id), `Missing learning content: ${word.id} (${word.word})`);
  return learning;
}

export function renderVocabularyWord(word, learning) {
  const dictionaryUrl = lookupWord => htmlText(`https://youdao.com/result?word=${encodeURIComponent(lookupWord)}&lang=en`);
  const dictionaryLink = (label, lookupWord = word.word) => {
    return `<a class="vocabulary-dictionary-link no-icon" href="${dictionaryUrl(lookupWord)}" target="_blank" rel="noopener noreferrer">${label}</a>`;
  };
  const highlight = text => text.split(wordPattern(word.word)).map((part, index) => index % 2 ? dictionaryLink(`<strong>${htmlText(part)}</strong>`) : htmlText(part)).join('');
  return `<details class="custom-block details vocabulary-word" data-word-id="${word.id}">\n` +
    `<summary><h4 id="word-${word.id}" class="vocabulary-word-title">${htmlText(word.word)}<a class="header-anchor" href="#word-${word.id}" aria-label="定位 ${htmlText(word.word)}">&#8203;</a></h4><button type="button" class="vocabulary-word-mark" data-mark-word="${word.id}" data-mark-label="${htmlText(word.word)}" aria-pressed="false" aria-label="${htmlText(word.word)}：红色，点击切换为绿色" title="${htmlText(word.word)}：红色，点击切换为绿色">🔴</button><span class="vocabulary-word-tools"><a class="vocabulary-dictionary-link vocabulary-word-dictionary no-icon" href="${dictionaryUrl(word.word)}" target="_blank" rel="noopener noreferrer" aria-label="在有道查询 ${htmlText(word.word)}" title="在有道查询 ${htmlText(word.word)}">🌐</a><span class="vocabulary-word-id">${word.id}</span></span></summary>\n` +
    `<div class="vocabulary-word-content">\n<p class="vocabulary-meaning">${htmlText(formatVocabularyMeaning(word.meaning))}</p>\n` +
    (learning.usageNote ? `<p class="vocabulary-usage"><span class="vocabulary-label">用法提示</span> ${htmlText(learning.usageNote)}</p>\n` : '') +
    `<p class="vocabulary-label">例句</p>\n<ol class="vocabulary-examples">\n` +
    learning.examples.map(example => `<li><p class="vocabulary-example-en" lang="en">${highlight(example.en)}</p><p class="vocabulary-example-zh" lang="zh-CN">${htmlText(example.zh)}</p></li>`).join('\n') +
    `\n</ol>\n<p class="vocabulary-label">常用搭配</p><p class="vocabulary-collocation"><span lang="en">${htmlText(learning.collocation[0])}</span> · ${htmlText(learning.collocation[1])}</p>\n` +
    `<p class="vocabulary-label">联想词</p><ul class="vocabulary-related">` + learning.related.map(related =>
      `<li><span class="vocabulary-relation">${htmlText(related.relation)}</span> <span lang="en">${dictionaryLink(htmlText(related.word), related.word)}</span> · ${htmlText(related.meaning)}</li>`
    ).join('') + `</ul>\n</div>\n</details>\n`;
}

// Each authored line surrounds exactly one canonical record marker. Definitions,
// links and coverage come from the handbook rather than a second copied word list.
export function compileVocabularyStories(chapters, stories) {
  assert.deepEqual(Object.keys(stories).sort(), chapters.map(chapter => chapter.id).sort(), 'Story chains must cover all 22 chapters');
  return Object.fromEntries(chapters.map(chapter => {
    const story = stories[chapter.id];
    assert(typeof story.title === 'string' && story.title.trim(), `Chapter ${chapter.id}: missing story title`);
    assert(Array.isArray(story.groups), `Chapter ${chapter.id}: missing story groups`);
    assert.deepEqual(story.groups.map(group => group.id), chapter.groups.map(group => group.id), `Chapter ${chapter.id}: story groups must follow the handbook`);
    const steps = [];
    const groups = chapter.groups.map((group, groupIndex) => {
      const lines = story.groups[groupIndex].lines;
      assert(Array.isArray(lines) && lines.length === group.words.length, `${group.id}: story must cover all ${group.words.length} records`);
      const start = steps.length;
      for (const [index, word] of group.words.entries()) {
        const line = lines[index];
        assert(typeof line === 'string', `${word.id}: missing story line`);
        const markers = [...line.matchAll(/\[\[(\d{2}-\d{3})\]\]/g)];
        assert.equal(markers.length, 1, `${word.id}: each story line must contain exactly one record marker`);
        const marker = markers[0];
        assert.equal(marker[1], word.id, `${word.id}: story words must follow the original record order`);
        const before = line.slice(0, marker.index);
        const after = line.slice(marker.index + marker[0].length);
        assert(!/\[\[|\]\]/.test(before + after), `${word.id}: malformed story marker`);
        assert(/[\p{Script=Han}]/u.test(before + after), `${word.id}: missing narrative context`);
        steps.push({id: word.id, word: word.word, meaning: formatVocabularyMeaning(word.meaning), before, after,
          groupId: group.id, groupTitle: group.title, groupStart: index === 0,
          href: `/vocabulary/chapter-${chapter.id}.html#word-${word.id}`});
      }
      return {id: group.id, title: group.title, start, end: steps.length, count: lines.length};
    });
    assert.equal(steps.length, chapter.records, `Chapter ${chapter.id}: incomplete story coverage`);
    return [chapter.id, {id: chapter.id, topic: chapter.title, title: story.title, groups, steps}];
  }));
}

export function validateVocabularyStories(chapters, stories) {
  compileVocabularyStories(chapters, stories);
}

function chapterPage(chapter, learning) {
  const links = chapter.groups.map(group => `- [${markdownLabel(group.title)}](#${group.id})`).join('\n');
  const [heading, ...body] = chapter.markdown.split('\n');
  const content = body.join('\n')
    .replace(/^\| 核对编号 \| 英文 \| 本主题简释及必要辨义 \|\n\| --- \| --- \| --- \|\n((?:\| \d{2}-\d{3} \|.*\|\n?)+)/gm, (_, table) =>
      [...table.matchAll(wordRow)].map(([, id, word, meaning]) => renderVocabularyWord({id, word, meaning}, learning.get(id))).join('\n'))
    .replace(groupHeading, (_, chapterId, groupId, title) =>
      `### 词群 ${chapterId}.${groupId}｜${title} {#group-${chapterId}-${groupId}}`
    );
  return frontmatter(`第 ${chapter.id} 章｜${chapter.title}`, true) + heading.replace(/^## /, '# ') +
    `\n\n[词汇学习总览](/vocabulary/) · [附录与来源](/vocabulary/appendices) · [单词故事接龙](/vocabulary/stories#story-${chapter.id})\n\n` +
    `点击单词展开中文释义、3 句例句、常用搭配与联想词。例句及关联表达为本站补充编写。\n\n` +
    `<VocabularyReader>\n\n## 本章词群\n\n${links}\n` + rewriteChapterLinks(content) + '\n\n</VocabularyReader>\n';
}

export async function generateVocabulary({source, clusters, stories, outputDir = path.join(root, 'site')} = {}) {
  source ??= await readFile(path.join(root, 'materials/vocabulary-handbook.md'), 'utf8');
  // Validate everything before touching output, so malformed input cannot replace good pages.
  const {overview, chapters, appendices, stats} = parseVocabulary(source);
  stories ??= Object.fromEntries(await Promise.all(chapters.map(async chapter => [chapter.id,
    JSON.parse(await readFile(path.join(root, `data/vocabulary-stories/chapter-${chapter.id}.json`), 'utf8')),
  ])));
  const compiledStories = compileVocabularyStories(chapters, stories);
  clusters ??= (await Promise.all(chapters.map(async chapter => JSON.parse(await readFile(path.join(root, `data/vocabulary-learning/chapter-${chapter.id}.json`), 'utf8'))))).flat();
  const learning = compileVocabularyLearning(chapters.flatMap(chapter => chapter.groups.flatMap(group => group.words)), clusters);
  const usageNotes = JSON.parse(await readFile(path.join(root, 'data/vocabulary-learning/usage-notes.json'), 'utf8'));
  for (const [id, note] of Object.entries(usageNotes)) {
    assert(learning.has(id) && typeof note === 'string' && note.trim(), `Invalid usage note: ${id}`);
    learning.get(id).usageNote = note;
  }
  const pages = new Map([
    ['index.md', frontmatter('词汇学习') + rewriteChapterLinks(overview) + '\n\n[阅读附录：重复词、义项说明与来源 →](/vocabulary/appendices)\n'],
    ['appendices.md', frontmatter('词汇附录与来源') + '# 词汇附录与来源\n\n[返回词汇学习总览](/vocabulary/)\n\n' + rewriteChapterLinks(appendices) + '\n'],
    ['stories.md', frontmatter('串学示范｜单词故事接龙互动').replace('pageClass: vocabulary-page', 'pageClass: vocabulary-page vocabulary-stories-page') +
      '# 串学示范｜单词故事接龙互动\n\n' +
      `<VocabularyStories :stories="${htmlText(JSON.stringify(chapters.map(chapter => compiledStories[chapter.id])))}" />\n`],
    ...chapters.map(chapter => [`chapter-${chapter.id}.md`, chapterPage(chapter, learning)]),
  ]);
  const directory = path.join(outputDir, 'vocabulary');
  await mkdir(directory, {recursive: true});
  for (const entry of await readdir(directory, {withFileTypes: true})) {
    if (entry.isFile() && entry.name.endsWith('.md') && !pages.has(entry.name)) await unlink(path.join(directory, entry.name));
  }
  for (const [name, content] of pages) await writeFile(path.join(directory, name), content);
  const sidebar = [
    {text: '词汇学习', items: [{text: '学习方法与主题总览', link: '/vocabulary/'}, {text: '单词故事接龙互动', link: '/vocabulary/stories'}]},
    {text: '22 个主题', items: chapters.map(chapter => ({text: `${chapter.id} · ${chapter.title}`, link: `/vocabulary/chapter-${chapter.id}`}))},
    {text: '附录', items: [{text: '重复词、义项说明与来源', link: '/vocabulary/appendices'}]},
  ];
  await mkdir(path.join(outputDir, '.vitepress'), {recursive: true});
  await writeFile(path.join(outputDir, '.vitepress/vocabulary-sidebar.json'), JSON.stringify(sidebar, null, 2) + '\n');
  return {...stats, pages: pages.size};
}
