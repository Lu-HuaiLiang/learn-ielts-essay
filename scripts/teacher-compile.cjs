'use strict';
const assert=require('node:assert/strict');
const model=require('../course-model.js');
const labels=new Set('观点 背景 解释 对比 情景 例子 结果 回扣 让步 反驳 条件 判断 定义 改写题目 表明立场'.split(' '));
const moveTitles={'观点':'确定这一段的判断','解释':'补上为什么','对比':'用差异支持判断','情景':'把观点放进情境','例子':'看例子证明了什么','结果':'推到具体结果','回扣':'回到本段核心点','让步':'保留另一面的合理性','反驳':'检验前面的推断','条件':'限定成立条件','判断':'给出这一层判断','定义':'先明确讨论的含义','改写题目':'摆出需要回答的争议','表明立场':'给出全文回答','背景':'界定问题背景'};
const methods=new Set('best only discussion advantages outweigh cause_effect cause_solution mixed degree abstract'.split(' '));
function validateTeaching(course,t) {
 const prefix=course.id+': ';
 assert.equal(t.id,course.id,prefix+'teacher ID');
 assert(methods.has(t.method),prefix+'unknown method');
 assert(t.task.focus && t.task.trap,prefix+'task analysis missing');
 assert(t.task.obligations.length>=2 && t.task.obligations.length<=4,prefix+'task obligations');
 assert(t.task.keywords.length>0,prefix+'task keywords missing');
 for(const k of t.task.keywords)assert(k.word && k.meaning && course.question.toLowerCase().includes(k.word.toLowerCase()),prefix+'keyword not in question: '+k.word);
 assert.equal(t.paragraphs.length,course.essay.length,prefix+'paragraph count');
 t.paragraphs.forEach((p,index)=>{
  assert(p.role && p.topic && p.controllingIdea && p.tools.length && p.coachQuestion && p.coachAnswer && p.check,prefix+'paragraph annotation incomplete '+index);
  assert(p.moves.length>0,prefix+'no sentence moves');
  const expected=course.essay[index].map((_,i)=>i);
  assert.deepEqual(p.moves.flatMap(m=>m.sentences),expected,prefix+'sentence coverage/order paragraph '+index);
  p.moves.forEach(m=>assert(m.sentences.length && labels.has(m.label) && m.note,prefix+'incomplete move'));
 });
 for(const key of ['opening','body','conclusion','limit'])assert(t.judgment[key],prefix+'judgment '+key);
}
function compileTeaching(course,t) {
 validateTeaching(course,t);
 const steps=[{kind:'overview',title:'审题：这道题要证明什么？',label:'先圈任务，再定方向',copy:t.task.focus,anchors:course.sentenceIds[0]}];
 t.paragraphs.forEach((p,index)=>p.moves.forEach((m,j)=>{
  steps.push({kind:'move',title:j===0?`第 ${index+1} 段 · ${p.role}`:moveTitles[m.label],label:`第 ${index+1} 段 / ${j+1} · ${m.label}`,copy:m.note,anchors:m.sentences.map(s=>course.sentenceIds[index][s]),paragraph:index,move:j,functionLabel:m.label,relation:m.relation || '',paragraphStart:j===0,paragraphEnd:j===p.moves.length-1, ...(j===p.moves.length-1?{corrections:(course.sourceCorrections || course.corrections || []).filter(c=>c.paragraphIndex===index)}:{})});
 }));
 steps.push({kind:'judgment',title:'核对：结尾兑现了开头吗？',label:'立场与论据',copy:'把题目、开头和结尾连起来看，再检验主体段能支持多强的判断。',anchors:[]});
 steps.push({kind:'practice',title:'合上范文，试着还原论证',label:'搭配与主动回忆',copy:'先用自己的话说清楚机制，再练习英文表达。',anchors:[]});
 const legacyStepMap=course.steps.map((s,i)=>i===0 || s.kind==='overview'?0:!s.anchors.length?steps.length-1:model.stepForSentence(steps,s.focus || s.anchors[0]));
 return {...course,teaching:t,teachingVersion:2,legacyStepMap,steps};
}
module.exports={validateTeaching,compileTeaching};
