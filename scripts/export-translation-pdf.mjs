import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdir, readFile, rename, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {groupEssays, learningText, loadEssays, questionTypes, root, validateTranslations, wordCount} from './essay-library.mjs';

const escape = text => String(text).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');

export function buildTranslationHtml({essays, translations, vocabulary, fontCss = ''}) {
  const {topics} = groupEssays(essays);
  validateTranslations(essays, translations);
  const paragraphCount = Object.values(translations).flat().length;
  const sentenceCount = Object.values(translations).flat(2).length;
  const toc = topics.map(topic => `<section class="toc-group">
    <div class="toc-topic">${escape(topic.title)} <span>${topic.essays.length} 篇</span></div>
    ${topic.essays.map(essay => `<a href="#${essay.id}"><span class="toc-code">${escape(essay.code)}</span><span>${escape(essay.title)}</span></a>`).join('')}
  </section>`).join('');
  const articles = topics.flatMap(topic => topic.essays).map(essay => {
    assert(Array.isArray(vocabulary[essay.id]), `${essay.id}: missing vocabulary highlights`);
    const pair = entry => `<div class="sentence-pair"><div class="sentence-en" lang="en">${learningText(entry.en, vocabulary[essay.id])}</div><div class="sentence-zh" lang="zh-CN">${escape(entry.zh)}</div></div>`;
    return `<article class="essay" id="${essay.id}">
      <div class="essay-kicker">${escape(essay.topic)} / ${escape(essay.topicEn)}</div>
      <h1><span class="essay-code">${escape(essay.code)}</span> ${escape(essay.title)}</h1>
      <div class="english-title" lang="en">${escape(essay.englishTitle)}</div>
      <div class="essay-meta">${escape(questionTypes.find(type => type.id === essay.questionType).title)} · ${wordCount(essay)} words</div>
      <section class="question-box"><div class="question-label">写作题目</div><div class="question" lang="en">${escape(essay.question)}</div></section>
      ${translations[essay.id].map((paragraph, i) => `<section class="essay-paragraph"><div class="paragraph-index">${String(i + 1).padStart(2, '0')}</div>${pair(paragraph[0])}${paragraph.length > 1 ? `<ul>${paragraph.slice(1).map(entry => `<li>${pair(entry)}</li>`).join('')}</ul>` : ''}</section>`).join('')}
    </article>`;
  }).join('');
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>雅思范文70篇 · 中英对照阅读</title><style>
    ${fontCss}
    @page { size: A4; margin: 20mm; }
    * { box-sizing: border-box; }
    html { color: #22252b; background: white; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    body { margin: 0; font-family: "Reading CJK", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; }
    [lang="en"] { font-family: "Reading Serif", Georgia, "Times New Roman", serif; }
    .cover { height: 245mm; display: flex; flex-direction: column; justify-content: center; break-after: page; }
    .cover-eyebrow { font: 10pt Georgia, serif; letter-spacing: 3px; color: #666; }
    .cover-rule { width: 30mm; height: 1mm; background: #6b429a; margin: 9mm 0; }
    .cover h1 { font-size: 32pt; font-weight: 600; margin: 0 0 5mm; line-height: 1.45; }
    .cover-subtitle { font-size: 18pt; color: #57505f; }
    .cover-stats { font-size: 11pt; color: #555; margin-top: 13mm; }
    .cover-note { margin-top: 28mm; font-size: 9.5pt; line-height: 1.9; color: #60636b; }
    .legend { margin-top: 4mm; font-size: 9pt; }
    .legend span + span { margin-left: 5mm; }
    .toc { break-after: page; }
    .toc h1 { font-size: 23pt; margin: 0 0 2mm; font-weight: 600; }
    .toc-intro { font-size: 9pt; color: #666; margin: 0 0 3mm; }
    .toc-columns { columns: 2; column-gap: 12mm; }
    .toc-group { break-inside: avoid; margin: 0 0 .8mm; }
    .toc-topic { font-size: 9.5pt; font-weight: 600; border-bottom: .3pt solid #dbd6e2; padding: 0 0 .5mm; margin-bottom: .5mm; }
    .toc-topic > span { font-size: 8pt; font-weight: 400; color: #777; margin-left: 2mm; }
    .toc a { display: flex; gap: 2mm; font-size: 8pt; line-height: 1.5; text-decoration: none; color: #303139; }
    .toc-code { flex: 0 0 12mm; color: #71627f; font-size: 8pt; }
    article.essay { break-before: page; }
    .essay-kicker { font-size: 9pt; color: #79668e; margin-bottom: 3mm; }
    .essay h1 { font-size: 20pt; font-weight: 600; margin: 0 0 2.5mm; line-height: 1.4; }
    .essay-code { font-size: 12pt; color: #777; font-weight: 400; margin-right: 2mm; }
    .english-title { font-size: 12pt; line-height: 1.5; color: #45434a; }
    .essay-meta { font-size: 8.5pt; color: #747078; margin: 3mm 0 6mm; }
    .question-box { border-left: 2pt solid #b5a4c5; background: #f7f5f9; padding: 3.5mm 4mm; margin-bottom: 6mm; break-inside: avoid; }
    .question-label { font-size: 8pt; color: #786985; margin-bottom: 1.5mm; }
    .question { font-size: 10pt; line-height: 1.6; }
    .essay-paragraph { margin: 0 0 5.5mm; }
    .paragraph-index { font: 8pt Georgia, serif; color: #93849f; margin-bottom: 2mm; break-after: avoid; }
    .sentence-pair { break-inside: avoid; }
    .sentence-en { font-size: 11pt; line-height: 1.7; overflow-wrap: anywhere; }
    .sentence-zh { font-size: 9.5pt; line-height: 1.8; color: #606168; margin-top: 1.2mm; overflow-wrap: anywhere; }
    .essay-paragraph ul { margin: 3mm 0 0; padding-left: 4.5mm; }
    .essay-paragraph li { padding-left: 1mm; margin: 0 0 3mm; break-inside: avoid; }
    .essay-paragraph li::marker { color: #9b94a2; font-size: 7pt; }
    .essay-learning { color: #ad313b; background: transparent; font-weight: 700; }
    .essay-repeated { color: #70419c; font-weight: 700; }
    p { orphans: 2; widows: 2; }
  </style></head><body>
    <section class="cover"><div class="cover-eyebrow">IELTS WRITING COLLECTION</div><div class="cover-rule"></div><h1>雅思范文 ${essays.length} 篇</h1><div class="cover-subtitle">中英对照阅读</div><div class="cover-stats">${topics.length} 个话题 · ${paragraphCount} 段 · ${sentenceCount} 句</div><div class="cover-note">英文逐句阅读，中文随句对照。<br>段首句独立呈现，其余句子按原有顺序分点排列。</div><div class="legend"><span class="essay-repeated">紫色 · 写作句架</span><span class="essay-learning">红色 · 重点词汇</span></div></section>
    <nav class="toc" aria-label="目录"><h1>目录</h1><p class="toc-intro">按话题编排 · 点击篇目可跳转至正文</p><div class="toc-columns">${toc}</div></nav>
    <main>${articles}</main>
  </body></html>`;
}

export async function exportTranslationPdf() {
  // Check the canonical source before creating or replacing the deliverable.
  execFileSync(process.execPath, [path.join(root, 'scripts/verify-essays.mjs')], {stdio: 'inherit'});
  const essays = await loadEssays();
  const translations = JSON.parse(await readFile(path.join(root, 'data/essay-translations.json'), 'utf8'));
  const vocabulary = JSON.parse(await readFile(path.join(root, 'data/essay-vocabulary.json'), 'utf8'));
  const fonts = await Promise.all(['regular', 'bold'].map(async (style, i) => {
    const data = await readFile(path.join(root, `mubu-editor/src/fonts/merriweather-${style}.woff2`));
    return `@font-face {font-family: "Reading Serif";font-style: normal;font-weight: ${i ? 700 : 400};src: url(data:font/woff2;base64,${data.toString('base64')}) format('woff2');}`;
  }));
  // An embedded TrueType CJK font preserves original Unicode when searching or copying.
  // macOS's native PingFang PDF fallback can encode common characters as CJK radicals.
  const cjkPath = process.env.PDF_CJK_FONT || '/System/Library/Fonts/Supplemental/Arial Unicode.ttf';
  const cjk = await readFile(cjkPath);
  fonts.push(`@font-face {font-family: "Reading CJK";font-style: normal;font-weight: 400;src: url(data:font/ttf;base64,${cjk.toString('base64')});}`);
  const html = buildTranslationHtml({essays, translations, vocabulary, fontCss: fonts.join('\n')});
  const tempDir = path.join(root, 'tmp/pdfs');
  const outputDir = path.join(root, 'output/pdf');
  await mkdir(tempDir, {recursive: true});
  await mkdir(outputDir, {recursive: true});
  await writeFile(path.join(tempDir, 'translation-reading.html'), html);
  const outputPath = path.join(outputDir, '雅思范文70篇-中英对照阅读.pdf');
  const temporaryPath = path.join(outputDir, '.translation-reading.partial.pdf');
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage();
    await page.setContent(html, {waitUntil: 'load'});
    await page.emulateMedia({media: 'print'});
    await page.evaluate(async () => { await document.fonts.ready; });
    assert(await page.evaluate(() => document.fonts.check('11pt "Reading Serif"')), 'Reading font did not load');
    assert(await page.evaluate(() => document.fonts.check('9.5pt "Reading CJK"')), 'Chinese reading font did not load');
    await page.pdf({
      path: temporaryPath,
      format: 'A4',
      preferCSSPageSize: true,
      printBackground: true,
      tagged: true,
      outline: true,
      margin: {top: '20mm', bottom: '20mm', left: '20mm', right: '20mm'},
      displayHeaderFooter: true,
      headerTemplate: '<div></div>',
      footerTemplate: '<div style="width:100%;margin:0 20mm;font:8px Arial;color:#888;display:flex;justify-content:space-between"><span>IELTS / BILINGUAL READING</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    });
    await rename(temporaryPath, outputPath);
  } finally {
    await browser.close();
  }
  console.log(`PDF exported: ${outputPath}`);
  return outputPath;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await exportTranslationPdf();
}
