/* Dependency-free desktop scrollytelling reader. */
(() => {
  'use strict';
  const { migrateProgress, selectStepAtLine, readingLineOffset, jumpScrollTop, stepForSentence, wordCount, filterCourses, nextCourse } = CourseModel;
  const $ = id => document.getElementById(id);
  const STORAGE_KEY = 'water-writing-lab.progress.v1';
  let raw = null;
  try { raw = localStorage.getItem(STORAGE_KEY); } catch { /* Reading works without storage. */ }
  const progress = migrateProgress(raw, COURSES);
  let course = COURSES.find(item => item.id === progress.course);
  let current = -1;
  let follow = true;
  let scrollFrame = 0;
  let lastLocationFrame = 0;
  let lastFocused = null;
  let stepElements = [];
  let tops = [];
  let libraryTopic = 'all';
  let libraryQuery = '';
  let libraryLastFocused = null;
  const topics = [...new Set(COURSES.map(c=>c.topic || '水资源'))];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const rich = text => escape(text).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/`([^`]+)`/g, '<code>$1</code>');
  const pad = n => String(n).padStart(2, '0');
  const sentenceById = id => {
    for (let p = 0; p < course.sentenceIds.length; p++) {
      const s = course.sentenceIds[p].indexOf(id);
      if (s >= 0) return course.essay[p][s];
    }
    return '';
  };
  function save() {
    progress.course = course.id;
    progress.steps[course.id] = current;
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(progress)); } catch { /* Optional enhancement. */ }
  }
  function copyParagraphs(text) {
    const sentences = text.match(/[^。]+。?|。/g) || [text];
    const groups = [];
    for (let i = 0; i < sentences.length; i += 2) groups.push(sentences.slice(i, i + 2).join(''));
    return groups.map(part => `<p>${rich(part)}</p>`).join('');
  }
  function roadmap() {
    return `<details class="roadmap"><summary>中文默写大纲 <span>展开 ＋</span></summary><ol class="outline-logic">${course.outline.map(line => {
      const [role, ...body] = line.split('：');
      return `<li><span class="outline-role">${escape(role)}</span>${rich(body.join('：'))}</li>`;
    }).join('')}</ol></details>`;
  }
  function collocations() {
    return `<div class="collocation-list">${course.collocations.map((item, i) => `<section class="collocation-card"><div class="collocation-heading"><span class="collocation-number">${pad(i + 1)}</span><h4 lang="en">${rich(item.phrase)}</h4></div><span class="source-tag">${escape(item.source)}</span><p class="usage">${rich(item.usage)}</p><div class="example" lang="en"><span class="example-label">TRANSFER · 自拟例句</span>${rich(item.example)}</div></section>`).join('')}</div>`;
  }
  function recall() {
    const other = nextCourse(COURSES, course.id);
    return `<div class="review-list">${course.questions.map((question, i) => `<details class="recall-item"><summary><span class="question-number">${i + 1}</span><span class="question-text">${rich(question)}</span><span class="answer-label">参考 ＋</span></summary><div class="answer">${rich(course.answers[i])}</div></details>`).join('')}</div><section class="transfer"><h4>换一个话题 · 写两三句</h4><p>${rich(course.transfer.replace(/^迁移：/, ''))}</p><textarea spellcheck="false" aria-label="迁移练习草稿" placeholder="先写中文逻辑，再尝试英文……"></textarea><small class="draft-note">自由练习区 · 草稿仅保留在当前页面，切课或刷新后清空</small><details><summary>展开自拟迁移示范</summary><p lang="en">${rich(course.transferAnswer)}</p></details></section><div class="course-complete">你已经读完本篇的论证、句法与搭配。下一步，尝试不看范文还原一段。<button class="switch-course" data-course="${other.id}"><span>继续学习 · ${other.title}</span><span aria-hidden="true">→</span></button></div><p class="method-note">逐句论证拆解参照所附六份课堂讲义；表达与练习结合 write-ielts-essays-my-style。讲解为重新编写，跨话题例句均为自拟。</p>`;
  }
  const methodNames = {best:'最佳方案比较',only:'责任范围检验',discussion:'双方依据与个人判断',advantages:'利弊分析',outweigh:'利弊权衡',cause_effect:'原因与影响',cause_solution:'原因与对策',mixed:'复合任务',degree:'程度与条件',abstract:'抽象观点具体化'};
  const functionTone = label => ['观点','表明立场','判断'].includes(label) ? 'point' : ['解释','对比'].includes(label) ? 'reason' : ['情景','例子'].includes(label) ? 'example' : ['结果','回扣'].includes(label) ? 'result' : ['让步','反驳','条件'].includes(label) ? 'challenge' : 'context';
  function taskLesson() {
    const t = course.teaching.task;
    // Highlight only literal spans of the source question, without interpreting its markup.
    const words = t.keywords.map(k=>k.word).sort((a,b)=>b.length-a.length);
    const pattern = new RegExp(words.map(w=>w.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('|'),'gi');
    let previous = 0, prompt = '';
    for (const match of course.question.matchAll(pattern)) {
      prompt += escape(course.question.slice(previous,match.index)) + `<mark>${escape(match[0])}</mark>`;
      previous = match.index + match[0].length;
    }
    prompt += escape(course.question.slice(previous));
    return `<blockquote class="task-prompt" lang="en">${prompt}</blockquote><div class="task-keywords">${t.keywords.map(k=>`<div><strong lang="en">${escape(k.word)}</strong><p>${rich(k.meaning)}</p></div>`).join('')}</div><div class="lesson-copy task-focus">${copyParagraphs(t.focus)}</div><ol class="task-obligations">${t.obligations.map(o=>`<li>${rich(o)}</li>`).join('')}</ol><aside class="scope-check"><span>审题提醒</span><p>${rich(t.trap)}</p></aside><div class="function-legend"><span class="point">观点</span><span class="reason">解释 / 对比</span><span class="example">例子 / 情景</span><span class="result">结果 / 回扣</span><span class="challenge">让步 / 条件</span></div><p class="class-note">参照所附讲义的拆题与论证方法编写。下面逐句看：这一步为什么能支持观点？</p><div class="scroll-cue"><span aria-hidden="true">↓</span>向下滚动，左侧跟随当前句子</div>`;
  }
  function correctionDetails(notes) {
    if (!notes?.length) return '';
    return `<details class="roadmap source-adjustments"><summary>这一段的表达小修 · ${notes.length} 处 <span>展开 ＋</span></summary>${notes.map(n=>`<section><h4>${escape(n.title)}</h4>${n.original?`<p class="source-quote" lang="en">原表达：${rich(n.original)}</p>`:''}${n.revised?`<p class="source-quote" lang="en">修订后：${rich(n.revised)}</p>`:''}<p>${rich(n.explanation)}</p></section>`).join('')}</details>`;
  }
  function moveLesson(step) {
    const p = course.teaching.paragraphs[step.paragraph];
    const tone = functionTone(step.functionLabel);
    const heading = step.paragraphStart ? `<div class="paragraph-plan"><div><span>TOPIC · 谈什么</span><p>${rich(p.topic)}</p></div><div><span>CONTROLLING IDEA · 往哪推</span><p>${rich(p.controllingIdea)}</p></div></div><div class="tool-tags"><span>本段展开</span>${p.tools.map(t=>`<b>${escape(t)}</b>`).join('')}</div>` : '';
    const close = step.paragraphEnd ? `<div class="paragraph-close"><details class="coach-question"><summary><span>停一下，想一想</span>${rich(p.coachQuestion)}<small>展开参考 ＋</small></summary><div>${rich(p.coachAnswer)}</div></details><aside class="scope-check"><span>论证边界</span><p>${rich(p.check)}</p></aside>${correctionDetails(step.corrections)}</div>` : '';
    return `${heading}<div class="function-card ${tone}"><div class="function-caption"><span class="function-tag">${escape(step.functionLabel)}</span><span>第 ${step.paragraph+1} 段 · 句 ${p.moves[step.move].sentences.map(i=>i+1).join('、')}</span></div><blockquote lang="en">${step.anchors.map(id=>rich(sentenceById(id))).join(' ')}</blockquote><div class="move-explanation">${copyParagraphs(step.copy)}</div>${step.relation?`<div class="language-link"><span>句内连接</span><p>${rich(step.relation)}</p></div>`:''}</div>${close}`;
  }
  function judgmentLesson() {
    const j=course.teaching.judgment;
    return `<div class="judgment-path">${[['opening','开头承诺'],['body','主体证明'],['conclusion','结尾回答']].map(([key,label],i)=>`<div><span>${pad(i+1)} · ${label}</span><p>${rich(j[key])}</p></div>`).join('')}</div><aside class="scope-check judgment-check"><span>这个结论能说多强？</span><p>${rich(j.limit)}</p></aside>${roadmap()}`;
  }
  function renderLesson(step, i) {
    const intro = i===0 ? `<div class="course-intro"><span class="eyebrow">IELTS WRITING / CLASSROOM NOTES / ${escape(course.code || course.number)}</span><h2>${escape(course.title)}</h2><div class="intro-meta"><span>${escape(methodNames[course.teaching.method])}</span><i class="meta-dot"></i><span>审题 → 逐句拆解 → 立场核对</span></div></div>` : '';
    const body = step.kind==='overview' ? taskLesson() : step.kind==='move' ? moveLesson(step) : step.kind==='judgment' ? judgmentLesson() : `<div class="lesson-copy">${copyParagraphs(step.copy)}</div><details class="practice-fold"><summary>搭配迁移 <span>${course.collocations.length} 组表达 ＋</span></summary>${collocations()}</details><details class="practice-fold"><summary>主动回忆与写作练习 <span>展开 ＋</span></summary>${recall()}</details>`;
    return `<section class="lesson ${i===0?'first':''} ${step.kind} ${step.paragraphStart?'paragraph-start':''} ${step.paragraphEnd?'paragraph-end':''}" id="lesson-${i}" data-step="${i}" aria-labelledby="lesson-title-${i}">${intro}<div class="lesson-label"><span class="chapter-number">${pad(i+1)}</span><span class="label-line"></span><span>${escape(step.label)}</span></div><h3 id="lesson-title-${i}">${escape(step.title)}</h3>${body}</section>`;
  }
  function render() {
    current = -1;
    document.title = `${course.title} · Essay 雅思写作精读`;
    $('course-tabs').innerHTML = `<div class="current-course"><span>${escape(course.topic || '水资源')} <i>·</i> ${escape(course.code || course.number)}</span><strong title="${escape(course.title)}">${escape(course.title)}</strong></div>`;
    $('collection-count').textContent = `${COURSES.length} ESSAYS`;
    $('library-total').textContent = COURSES.length;
    $('essay-title').textContent = course.englishTitle || (course.id === 'conservation' ? 'Water conservation' : 'The right to water');
    $('word-count').textContent = `${wordCount(course.essay)} WORDS`;
    $('essay-question').textContent = course.question;
    $('question-note').textContent = course.questionNote || '';
    $('essay-prompt').open = false;
    $('word-count').title = course.declaredWords && course.declaredWords !== wordCount(course.essay) ? `原材料标注 ${course.declaredWords} 词；本页按正文重新计算，不改动英文。` : '按空格分词，连字符词及缩写计为一词，不计单独标点';
    $('essay').innerHTML = course.essay.map((paragraph, p) => `<section class="essay-paragraph"><div class="paragraph-label"><span class="pnumber">${pad(p + 1)}</span>${escape(course.paragraphLabels[p])}</div><p>${paragraph.map((sentence, s) => `<span role="button" tabindex="0" class="sentence" id="${course.sentenceIds[p][s]}" data-sentence="${course.sentenceIds[p][s]}" aria-label="查看此句讲解：${escape(sentence.replace(/\*\*/g,''))}">${rich(sentence)}</span>`).join(' ')}</p></section>`).join('');
    $('teaching').innerHTML = course.steps.map(renderLesson).join('');
    $('section-rail').innerHTML = course.steps.map((step, i) => `<button class="rail-dot" data-jump="${i}" aria-label="第 ${i + 1} 节：${escape(step.title)}" title="${pad(i + 1)} ${escape(step.title)}"></button>`).join('');
    $('outline-list').innerHTML = course.steps.map((step, i) => `<button class="outline-entry" data-jump="${i}"><span class="outline-num">${pad(i + 1)}</span><span>${escape(step.title)}</span></button>`).join('');
    stepElements = [...document.querySelectorAll('.lesson')];
    $('essay-scroll').scrollTop = 0;
    measure();
  }
  function measure() { tops = stepElements.map(element => element.getBoundingClientRect().top + scrollY); }
  function readingLine() {
    const styles = getComputedStyle(document.documentElement);
    return scrollY + readingLineOffset(innerHeight, parseFloat(styles.getPropertyValue('--header')), parseFloat(styles.getPropertyValue('--footer')));
  }
  function ensureEnglishVisible(anchors, immediate = false) {
    if (!follow || !anchors.length) return;
    const pane = $('essay-scroll');
    const visible = pane.getBoundingClientRect();
    const first = $(anchors[0]);
    if (!first) return;
    const firstBox = first.getBoundingClientRect();
    const last = $(anchors[anchors.length - 1]).getBoundingClientRect();
    const tooTall = last.bottom - firstBox.top > pane.clientHeight - 70;
    if (firstBox.top < visible.top + 24 || firstBox.top > visible.bottom - 80 || (!tooTall && last.bottom > visible.bottom - 28)) {
      const paragraph = first.closest('.essay-paragraph');
      const label = paragraph.querySelector('.paragraph-label').getBoundingClientRect();
      const targetTop = firstBox.top - label.bottom < 20 ? label.top : firstBox.top;
      pane.scrollTo({top: Math.max(0, pane.scrollTop + targetTop - visible.top - 28), behavior: immediate || reduced.matches ? 'instant' : 'smooth'});
    }
  }
  function activate(index, immediate = false) {
    index = Math.max(0, Math.min(index, course.steps.length - 1));
    if (index === current) return;
    current = index;
    const step = course.steps[index];
    document.querySelectorAll('.sentence').forEach(el => el.classList.toggle('is-active', step.anchors.includes(el.id)));
    stepElements.forEach((el, i) => {
      el.classList.toggle('is-current', i === index);
      if (i === index) el.setAttribute('aria-current', 'step');
      else el.removeAttribute('aria-current');
    });
    document.querySelectorAll('[data-jump]').forEach(el => {
      if (+el.dataset.jump === index) el.setAttribute('aria-current', 'step');
      else el.removeAttribute('aria-current');
    });
    $('previous').disabled = index === 0;
    $('next').disabled = index === course.steps.length - 1;
    $('step-position').textContent = `${pad(index + 1)} / ${pad(course.steps.length)}`;
    $('progress-fill').style.width = `${(index + 1) / course.steps.length * 100}%`;
    const focusAnchors = step.focus ? step.anchors.slice(step.anchors.indexOf(step.focus)) : step.anchors;
    ensureEnglishVisible(focusAnchors, immediate);
    save();
  }
  function jump(index, immediate = false) {
    measure();
    index = Math.max(0, Math.min(index, course.steps.length - 1));
    const header = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header'));
    // Instant jumps keep chapter selection deterministic; ordinary reading remains native scrolling.
    const footer = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--footer'));
    const target = jumpScrollTop(tops[index], stepElements[index].getBoundingClientRect().height, readingLineOffset(innerHeight, header, footer), header);
    window.scrollTo({top: index === 0 ? 0 : target, behavior:'instant'});
    activate(index, immediate);
  }
  function changeCourse(id) {
    if (id === course.id) { closeLibrary(); return; }
    save();
    closeOutline(false);
    closeLibrary(false);
    cancelAnimationFrame(scrollFrame);
    const nextCourse = COURSES.find(item => item.id === id);
    if (!nextCourse) return;
    course = nextCourse;
    render();
    jump(progress.steps[id], true);
    $('library-toggle').focus({preventScroll:true});
  }
  function openOutline() {
    closeLibrary(false);
    lastFocused = document.activeElement;
    $('outline-panel').hidden = false;
    $('outline-backdrop').hidden = false;
    $('outline-toggle').setAttribute('aria-expanded','true');
    const active = $('outline-list').querySelector('[aria-current=step]');
    (active || $('outline-close')).focus({preventScroll:true});
    active?.scrollIntoView({block:'nearest', behavior:'instant'});
  }
  function renderLibrary() {
    const results = filterCourses(COURSES, {query:libraryQuery, topic:libraryTopic});
    $('library-subtitle').textContent = `${topics.length} 个话题 / ${COURSES.length} 篇范文`;
    $('library-result-count').textContent = `${libraryTopic === 'all' ? '全部话题' : libraryTopic} · ${results.length} 篇`;
    $('library-clear').hidden = !libraryQuery;
    $('library-topics').querySelectorAll('[data-topic]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.topic === libraryTopic)));
    $('library-results').innerHTML = results.length ? results.map(item=>{
      const step = progress.steps[item.id];
      const status = item.id === course.id ? '当前课程' : step > 0 ? `学至 ${pad(step+1)} / ${pad(item.steps.length)}` : '开始学习';
      return `<button class="library-card ${item.id === course.id ? 'is-selected' : ''}" data-course="${escape(item.id)}"><div class="library-card-meta"><span>${escape(item.topic || '水资源')} <i>·</i> ${escape(item.code || item.number)}</span><small>${wordCount(item.essay)} 词</small></div><h3>${escape(item.title)}</h3><p>${escape(item.type)}</p><div class="library-card-footer"><span>${escape(status)}</span><span aria-hidden="true">→</span></div></button>`;
    }).join('') : '<div class="library-empty"><span>没有找到匹配课程</span><p>换一个关键词，或切换到全部话题。</p></div>';
  }
  function openLibrary() {
    libraryLastFocused = document.activeElement;
    closeOutline(false);
    $('library-panel').hidden = false;
    $('library-backdrop').hidden = false;
    $('library-toggle').setAttribute('aria-expanded','true');
    document.body.style.overflow = 'hidden';
    if (!$('library-topics').children.length) {
      $('library-topics').innerHTML = `<button data-topic="all" aria-pressed="true"><span>全部话题</span><small>${COURSES.length}</small></button>` + topics.map(topic=>`<button data-topic="${escape(topic)}" aria-pressed="false"><span>${escape(topic)}</span><small>${COURSES.filter(c=>(c.topic || '水资源') === topic).length}</small></button>`).join('');
    }
    renderLibrary();
    $('library-search').focus({preventScroll:true});
  }
  function closeLibrary(restore = true) {
    const wasOpen = !$('library-panel').hidden;
    $('library-panel').hidden = true;
    $('library-backdrop').hidden = true;
    $('library-toggle').setAttribute('aria-expanded','false');
    if (wasOpen) document.body.style.overflow = '';
    if (wasOpen && restore && libraryLastFocused?.isConnected) libraryLastFocused.focus({preventScroll:true});
  }
  function closeOutline(restore = true) {
    const wasOpen = !$('outline-panel').hidden;
    $('outline-panel').hidden = true;
    $('outline-backdrop').hidden = true;
    $('outline-toggle').setAttribute('aria-expanded','false');
    if (wasOpen && restore && lastFocused?.isConnected) lastFocused.focus({preventScroll:true});
  }
  document.addEventListener('click', event => {
    const target = event.target.closest('button, [data-sentence]');
    if (!target) return;
    if (target.dataset.course) changeCourse(target.dataset.course);
    if (target.dataset.topic) { libraryTopic = target.dataset.topic; renderLibrary(); }
    if (target.dataset.jump != null) {
      jump(+target.dataset.jump);
      closeOutline();
    }
    if (target.dataset.sentence) jump(stepForSentence(course.steps, target.dataset.sentence));
  });
  $('essay').addEventListener('keydown', event => {
    if (event.target.dataset.sentence && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      jump(stepForSentence(course.steps, event.target.dataset.sentence));
    }
  });
  $('library-toggle').addEventListener('click', openLibrary);
  $('library-close').addEventListener('click', ()=>closeLibrary());
  $('library-backdrop').addEventListener('click', ()=>closeLibrary());
  $('library-search').addEventListener('input', event=>{ libraryQuery = event.target.value; renderLibrary(); });
  $('library-clear').addEventListener('click', ()=>{libraryQuery='';$('library-search').value='';renderLibrary();$('library-search').focus();});
  $('previous').addEventListener('click', () => jump(current - 1));
  $('next').addEventListener('click', () => jump(current + 1));
  $('brand-home').addEventListener('click', event => { event.preventDefault(); jump(0); });
  $('outline-toggle').addEventListener('click', () => $('outline-panel').hidden ? openOutline() : closeOutline());
  $('outline-close').addEventListener('click', () => closeOutline());
  $('outline-backdrop').addEventListener('click', () => closeOutline());
  $('restart').addEventListener('click', () => { jump(0); closeOutline(); });
  $('follow-toggle').addEventListener('click', () => {
    follow = !follow;
    $('follow-toggle').setAttribute('aria-pressed', String(follow));
    if (follow) ensureEnglishVisible(course.steps[current].anchors);
  });
  document.addEventListener('keydown', event => {
    if (!$('library-panel').hidden) {
      if (event.key === 'Escape') {event.preventDefault();closeLibrary();}
      if (event.key === 'Tab') {
        const items = [...$('library-panel').querySelectorAll('button:not([hidden]), input')];
        if (event.shiftKey && document.activeElement === items[0]) {event.preventDefault();items.at(-1).focus();}
        else if (!event.shiftKey && document.activeElement === items.at(-1)) {event.preventDefault();items[0].focus();}
      }
      return;
    }
    if ($('outline-panel').hidden) return;
    if (event.key === 'Escape') { event.preventDefault(); closeOutline(); }
    if (event.key === 'Tab') {
      const buttons = [...$('outline-panel').querySelectorAll('button')];
      if (event.shiftKey && document.activeElement === buttons[0]) { event.preventDefault(); buttons.at(-1).focus(); }
      else if (!event.shiftKey && document.activeElement === buttons.at(-1)) { event.preventDefault(); buttons[0].focus(); }
    }
  });
  window.addEventListener('scroll', () => {
    cancelAnimationFrame(scrollFrame);
    scrollFrame = requestAnimationFrame(() => activate(selectStepAtLine(tops, readingLine())));
  }, {passive:true});
  const resizeObserver = new ResizeObserver(() => {
    cancelAnimationFrame(lastLocationFrame);
    lastLocationFrame = requestAnimationFrame(() => measure());
  });
  resizeObserver.observe($('teaching'));
  window.addEventListener('resize', () => { measure(); activate(selectStepAtLine(tops, readingLine())); });
  $('essay-prompt').addEventListener('toggle', () => ensureEnglishVisible(course.steps[current]?.anchors || []));
  render();
  jump(progress.steps[course.id], true);
})();
