(function (root) {
  'use strict';
  function restoreProgress(raw, limits) {
    const ids = Object.keys(limits);
    const result = { course: ids[0], steps: Object.fromEntries(ids.map(id => [id, 0])) };
    let saved;
    try { saved = JSON.parse(raw); } catch { return result; }
    if (!saved || typeof saved !== 'object' || Array.isArray(saved)) return result;
    if (Object.hasOwn(limits, saved.course)) result.course = saved.course;
    for (const id of ids) {
      const index = saved.steps?.[id];
      if (Number.isInteger(index)) result.steps[id] = Math.max(0, Math.min(index, limits[id] - 1));
    }
    return result;
  }
  function migrateProgress(raw, courses) {
    const limits = Object.fromEntries(courses.map(c=>[c.id,c.steps.length]));
    const result = restoreProgress(raw, limits);
    let saved;
    try { saved = JSON.parse(raw); } catch { saved = null; }
    if (saved && saved.teachingVersion !== 2) {
      for (const c of courses) {
        const old = saved.steps?.[c.id];
        if (Number.isInteger(old) && c.legacyStepMap?.length) {
          result.steps[c.id] = c.legacyStepMap[Math.max(0, Math.min(old, c.legacyStepMap.length - 1))];
        }
      }
    }
    return {...result, teachingVersion:2};
  }
  function selectStepAtLine(tops, line) {
    let current = 0;
    for (let i = 0; i < tops.length; i++) {
      if (tops[i] <= line) current = i;
      else break;
    }
    return current;
  }
  function readingLineOffset(viewport, header, footer) {
    return header + Math.max(0, viewport - header - footer) * 0.5;
  }
  function jumpScrollTop(top, height, offset, header) {
    const inset = Math.min(Math.max(0, offset - header - 32), height * 0.5);
    return Math.max(0, top + inset - offset);
  }
  function stepForSentence(steps, id) {
    let selected = 0;
    let narrowest = Infinity;
    steps.forEach((step, index) => {
      if (step.kind !== 'overview' && step.anchors.includes(id) && step.anchors.length < narrowest) {
        selected = index;
        narrowest = step.anchors.length;
      }
    });
    return selected;
  }
  function wordCount(paragraphs) {
    return paragraphs.flat().join(' ').replace(/\*\*/g, '').trim().split(/\s+/).filter(token=>/[\p{L}\p{N}]/u.test(token)).length;
  }
  function filterCourses(courses, {query = '', topic = 'all'} = {}) {
    const terms = query.normalize('NFKC').toLowerCase().trim().split(/\s+/).filter(Boolean);
    return courses.filter(item => {
      if (topic !== 'all' && item.topic !== topic) return false;
      const text = [item.code, item.title, item.englishTitle, item.topic, item.topicEn, item.type, item.question, item.position].filter(Boolean).join(' ').normalize('NFKC').toLowerCase();
      return terms.every(term => text.includes(term));
    });
  }
  function nextCourse(courses, id) {
    return courses[(courses.findIndex(item => item.id === id) + 1) % courses.length];
  }
  const api = { restoreProgress, migrateProgress, selectStepAtLine, readingLineOffset, jumpScrollTop, stepForSentence, wordCount, filterCourses, nextCourse };
  root.CourseModel = api;
  if (typeof module !== 'undefined') module.exports = api;
})(globalThis);
