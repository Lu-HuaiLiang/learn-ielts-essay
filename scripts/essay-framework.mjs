// Curated from write-ielts-essays-my-style/references/{outlines,
// teacher-expression-core, teacher-expression-nine-topic-core,
// teacher-expression-five-topic-core}.md, checked against the current essays.
// Each capture marks a reusable fragment; text between captures is a topic slot.
// Keep the rules here so generating the site never needs the Downloads skill.
const rules = [
  // Background and debate.
  /\b(has thrived (?:for (?:many )?years|in recent years))\b/dgiu,
  /\b(has grown significantly in)\b/dgiu,
  /\b(Opinions (?:differ|vary) (?:as to|regarding))\b/dgiu,
  /\b((?:There (?:has been|is) a|A) fierce(?: (?:yet|and) unresolved)? debate(?: (?:rages|remains))? (?:as to|over|about|concerning))\b/dgiu,
  /\b((?:One of the|A) (?:worrying|growing) (?:trends?|issues?) in modern society is(?: that)?)\b/dgiu,
  /\b(The (?:importance|significance) of)\b[^.!?;\n]+?\b(is (?:beyond doubt|clear|unquestionable))\b/dgiu,
  /\b(The fact that)\b[^.!?;\n]+?\b(has led to the proposal that)\b/dgiu,
  /\b(with such benefits comes a proposal that)\b/dgiu,

  // Topic sentences: reasons, benefits, objections and the other view.
  /\b(The primary justification for)\b[^.!?;\n]+?\b((?:has traditionally resided|lies|resides) in(?: the (?:belief|fact) that)?|is that)\b/dgiu,
  /\b(The argument (?:in favou?r of|against|for))\b[^.!?;\n]+?\b(is that|is|lies in)\b/dgiu,
  /\b(The primary objection to)\b[^.!?;\n]+?\b(is that)\b/dgiu,
  /\b(The (?:primary|compelling|underlying) reason(?: for)?)\b[^.!?;\n]*?\b(lies in the fact that|is that)\b/dgiu,
  /\b((?:One|The main) reason for)\b[^.!?;\n]+?\b(is that|is)\b/dgiu,
  /\b((?:The main|A major) cause of)\b[^.!?;\n]+?\b(can be|is)\b/dgiu,
  /\b(One (?:of the )?(?:tangible benefits?|drawbacks?|demerits?) of)\b[^.!?;\n]+?\b(is that|is)\b/dgiu,
  /\b(One (?:major )?factor(?: contributing to)?)\b[^.!?;\n]*?\b(is that|is)\b/dgiu,
  /\b(Another (?:reason|factor)(?: is that| is)?)\b/dgiu,
  /\b(Others, however, (?:highlight|claim that|argue that|point out that))\b/dgiu,
  /\b((?:occurs?|happens?) for several reasons)\b/dgiu,
  /\b((?:the )?foremost of which (?:is|are))\b/dgiu,

  // Concession, testing assumptions and limiting the inference.
  /\b(Although|Even though|Despite|Admittedly)\b/dgiu,
  /\b(can be justified due to the benefits that accrue to)\b/dgiu,
  /\b(the risk of)\b[^.!?;\n]+?\b(makes it imperative to)\b/dgiu,
  /\b(reaching such a conclusion)\b/dgiu,
  /\b((?:does|do) not necessarily (?:mean(?: that)?|amount to|justify))\b/dgiu,
  /\b(does not mean that)\b/dgiu,
  /\b((?:is|are) based on the (?:(?:questionable|erroneous) )?assumption that)\b/dgiu,
  /\b((?:(?:is|are) grounded|rests?|resting) on the (?:premise|assumption) that)\b/dgiu,
  /\b((?:overlooks?|ignores?) the (?:fact|possibility) that)\b/dgiu,
  /\b(not everyone (?:is convinced by|finds this convincing))\b/dgiu,
  /\b(it is worthwhile to point out that)\b/dgiu,
  /\b(such benefits cannot justify)\b/dgiu,

  // Explanation, examples, hypothetical consequences and opportunity costs.
  /\b(This is because|As a result|For example|For instance|In the past|By contrast|In contrast)\b/dgiu,
  /\b(A (?:good|typical) example can be found in)\b/dgiu,
  /\b(If this (?:proposal|policy|idea|measure) were (?:to be )?(?:adopted|implemented))\b/dgiu,
  /\b((?:would|could) otherwise (?:be spent(?: on)?|be used(?: to|for)?))\b/dgiu,
  /\b(Given that|considering the fact that|provided that)\b/dgiu,
  /\b(all of which|both of which|some of which)\b/dgiu,
  /\b(not only)\b[^.!?;\n]+?\b(but also)\b/dgiu,
  /\b(ranging from)\b[^.!?;\n]+?\b(to)\b/dgiu,
  /\b(be it|be they|albeit to varying degrees)\b/dgiu,
  /\b(Central to)\b[^.!?;\n]+?\b(is|are)\b/dgiu,
  /\b(With)\b[^.!?;\n]+?\b((?:also )?comes?)\b/dgiu,
  /\b(Only (?:by|when|with))\b[^.!?;\n]+?\b(can|could|will)\b/dgiu,
  /\b(So interconnected is)\b[^.!?;\n]+?\b(that)\b/dgiu,
  /\b(Long gone are the days when)\b/dgiu,
  /\b(The same principle applies(?: to)?)\b/dgiu,

  // Overall judgement and closing the argument.
  /\b(In conclusion|On balance|In my view|In addition)\b/dgiu,
  /\b(I (?:think|believe|would argue) that|it is my opinion that)\b/dgiu,
  /(?:^|[.!?]\s+)(I think|I believe)\b/dgiu,
  /\b(I (?:largely |partly )?(?:agree|disagree) with (?:this|the) view)\b/dgiu,
  /\b(I find the second view more convincing because)\b/dgiu,
  /\b((?:I think )?it is better to seek a compromise between the two (?:views|sides))\b/dgiu,
  /\b(rather than take either position to extremes)\b/dgiu,
  /\b(It seems, therefore, sensible to)\b/dgiu,
  /\b((?:is|are) (?:still )?justifi(?:ed|able) in view of)\b/dgiu,
];

export function frameworkRanges(text) {
  const ranges = rules.flatMap(pattern =>
    [...text.matchAll(pattern)].flatMap(match => match.indices.slice(1))
  ).sort((a, b) => a[0] - b[0] || b[1] - a[1]);
  const merged = [];
  for (const [start, end] of ranges) {
    const previous = merged.at(-1);
    if (previous && start <= previous[1]) previous[1] = Math.max(previous[1], end);
    else merged.push([start, end]);
  }
  return merged;
}
