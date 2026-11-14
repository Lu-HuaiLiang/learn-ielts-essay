"""Extract the supplied revised essays verbatim and add authored teaching material."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'materials/nine-topics.md').read_text()
records = []
headings = list(re.finditer(r'^## 第(\d+)篇 (.+?) (\d+)词$', SOURCE, re.M))
anchors = [[1,1,2],[1,2,3],[0,1,2],[1,1,3],[1,2,3],[1,2,3],[0,1,3],[2,1,3],[1,2,2],[1,2,2],[1,2,3],[0,1,4],[0,1,2],[2,3,4],[1,2,2],[1,2,3],[1,2,2],[1,2,3],[1,2,0],[0,1,2],[1,2,3],[1,2,2],[1,2,3],[1,2,3],[2,2,3],[1,3,4]]
correction_titles = [
 ['适应行动与被动习惯','屋顶绿化的降温目的','停止升温与限制升温'],
 ['替代食品的可获得性','医学研究的必要条件','大类、成员与生产规模'],
 ['比较标准补完整','适者并非最强壮者','预算机会成本须有条件'],
 ['情态动词后的被动','紧迫性与生态价值','整体保护不等于等额投入'],
 ['用where连接地点与机制','从意识落实到拒买','take a heavy toll on'],
 ['中产群体扩大','from A to B范围结构','倒装中的复数主语'],
 ['恢复句界与让步主句','旅游并非唯一发展途径','负面影响与旅游的主语分开'],
 ['回答能否替代亲历学习','在家查阅的自然搭配','信息传递与个人体验'],
 ['久坐链条与因果强度','适度使用才支持无害娱乐','历史情景与虚构边界'],
 ['过去游戏平台的范围','奖励机制而非医学断言','陪伴家人与培养爱好'],
 ['区分现实与虚构','非必要条件不等于无害','教育效果须有内容条件'],
 ['间接疑问句与角色搭配','按个人能力评估适岗性','can play与already play'],
 ['传统分工正在改变','收入比较接回父亲留家','instead前用分号'],
 ['配额限制名额而非强制分科','歧视与偏好可以并存','尊重选择同时去除障碍'],
 ['in favour of不可缺in','不足与适得其反有别','照护责任相关歧视'],
 ['跨文化共鸣保留可能性','功能不等于严格定义','关系从句补出谓语'],
 ['背景音乐的自然表达','trigger与bring分别搭配','最重要须建立比较标准'],
 ['提供经费而非购买金钱','共同出资与使用程度','允许额外私人服务'],
 ['financial后接名词','贷款回收不等于零成本','全额学费与所有资助有别'],
 ['共同责任仍然是同意','广告到饮食的中间机制','屏幕使用的时间机会成本'],
 ['竞争场景而非唯一社会法则','compromise不是comprise','achieve接目标并收窄绝对判断'],
 ['So...that倒装与责任范围','效果有限不等于不可行','独立本地行动回应only'],
 ['burden on与成本清单','赛事展示、参与者学习','总收入不能推出净利润'],
 ['athletes才是发挥的主体','坚持与战胜的准确搭配','much better与复数limits'],
 ['the number配small','聚光灯内的隐私压力','市场收入到公平报酬的桥接'],
 ['薪水与薪水作比较','假设研发例子取代未核验史实','结尾与反对高薪立场统一']
]

for i, h in enumerate(headings):
    block = SOURCE[h.end():headings[i+1].start() if i+1 < len(headings) else SOURCE.index('# 九个话题共通的修改原则')].strip()
    block = re.split(r'^# ', block, maxsplit=1, flags=re.M)[0].strip()
    question_part, correction_part = block.split('**最值得理解的三处调整**', 1)
    sections = [p.strip() for p in question_part.split('\n\n') if p.strip()]
    assert sections.pop(0) == '**原题**'
    question = sections.pop(0)
    if sections[0].startswith('**本篇调整说明**'):
        sections.pop(0)
    paragraphs = sections
    topic = list(re.finditer(r'^# ([^\n]+?) ([A-Za-z ]+)$', SOURCE[:h.start()], re.M))[-1]
    corrections = []
    cparts = re.split(r'\*\*[123]．\*\* 原文：', correction_part)[1:]
    for j, part in enumerate(cparts):
        original_part, revised_part = part.split('修改后：', 1)
        chunks = revised_part.strip().split('\n\n', 1)
        def quote(s):
            return '\n'.join(re.sub(r'^> ?', '', line) for line in s.strip().splitlines())
        corrections.append(dict(title=correction_titles[i][j], original=quote(original_part), revised=quote(chunks[0]), explanation=chunks[1].strip(), paragraphIndex=anchors[i][j]))
    assert len(corrections) == 3, h.group(0)
    records.append(dict(id=f'nine-{i+1:02}', code=f'N{i+1:02}', title=h.group(2), sourceHeading=h.group(0), declaredWords=int(h.group(3)), sourceGroup='nine', topic=topic.group(1), topicEn=topic.group(2), question=question, essayParagraphs=paragraphs, corrections=corrections))

def add(n, english_title, task_type, position, notes, collocations, qa, transfer, transfer_answer):
    r = records[n-1]
    r.update(englishTitle=english_title, type=task_type, position=position)
    r['paragraphNotes'] = []
    for line in notes.strip().splitlines():
        role, explanation, chain = line.split('|')
        r['paragraphNotes'].append(dict(role=role, explanation=explanation, chain=chain.split('→')))
    r['collocations'] = []
    for line in collocations.strip().splitlines():
        phrase, source, usage, example = line.split('|')
        source = {'熟':'熟悉（讲义）','校':'校正','补':'通用补充'}[source]
        r['collocations'].append(dict(phrase=phrase, source=source, usage=usage, example=example))
    pairs = [line.split('|') for line in qa.strip().splitlines()]
    r['questions'] = [p[0] for p in pairs]
    r['answers'] = [p[1] for p in pairs]
    r.update(transfer=transfer, transferAnswer=transfer_answer)

add(1, 'Climate Change: Adaptation and Prevention', '同意程度题', '部分同意适应已有变化；不同意用适应取代预防，应同时限制进一步升温。', '''
开头：区分目标|承认天气变化难以短期解决，但把预防对象写成进一步升温，避免将已经发生的变化说成能全部撤销。|全球气候变化难处理→需要适应当前影响→仍需预防进一步升温
主体一：适应的可行性|能源消耗、工业排放等难立刻消失，所以用遮阴、屋顶绿化和反射路面减轻建筑与街道高温；适应是行动而非习惯。|成因难短期消除→种树与屋顶绿化→减少建筑吸热→浅色路面反射阳光→降低当前热影响
主体二：预防仍有价值|提升能效限制能源消耗增长，替代能源减少化石燃料依赖；不能彻底停止变化，不等于小幅减缓没有价值。|提高能效→放慢化石燃料燃烧→发展替代能源→限制进一步升温→减少未来损害
结尾：双轨答案|可持续发展既要承受眼前变化，也要减少未来损害；结尾保留两项措施，不用适应成功否定减排。|适应当前情况→预防进一步升温→共同支持可持续发展
''', '''
adapt to|校|主动调整以适应；adapt to + N/V-ing，to是介词。|New employees may need time to adapt to working with an international team.
alleviate its effects|校|减轻后果而非消除根源；alleviate + effects of N，its须有清楚指代。|Long commutes may cause fatigue, but flexible hours can alleviate its effects.
reduce reliance|校|降低依赖；reduce reliance on + N/V-ing。|Better buses could reduce reliance on private cars.
alternative energy sources|校|指出替代资源；alternative + N，sources可用作develop的宾语。|Schools could explore alternative funding sources before raising tuition fees.
should never be underestimated|校|强调不应低估；N + should never be underestimated，被动后不再加宾语。|The value of regular feedback should never be underestimated in language learning.
''', '''
为什么be accustomed to不能说明适应措施降低损害？|它只表示习惯；adapt to包含调整行为，遮阴和绿化才能解释高温影响如何减少。
主体二如何从能源效率接到预防目标？|能效提升限制能源消耗增长，放慢燃烧化石燃料；替代能源再减少依赖，从而限制进一步升温。
本文为何承认短期无法彻底停止变化，却仍支持预防？|完全停止与限制进一步升温是不同目标，前者困难不取消后者减少未来损害的价值。
''', '换成城市拥堵：用两句区分适应当前拥堵与减少未来拥堵，写出具体措施。', 'Flexible working hours can help commuters adapt to current congestion. Cities should also improve bus services to reduce reliance on private cars and limit future traffic growth.')

add(2, 'Animal Use for Food, Medicine and Clothing', '同意程度题', '不同意一概停止：食物和医药在仍有必要且缺少替代时可合理使用动物；反对仅为皮毛屠杀。', '''
开头：用途分类|动物有生命权，但不是每种利用都同样必要；先提出有条件允许与禁止并存，后文按用途检验。|承认动物生命权→判断用途必要性→部分利用可辩护→部分实践不可接受
主体一：食物替代的边界|农业发展让许多人可采用植物性饮食，但不能假设所有人立即获得营养充分的替代食物，因此拒绝全球一刀切。|植物性食物可提供营养→许多人可以替代肉食→充分替代品尚非人人可得→不能要求立即全面停食
主体二：医学条件|致命疾病研究的必要性须与缺少已验证替代方案相结合，并加上人道对待；不是动物死亡与人死亡的必然二选一。|严重疾病研究需求→有效替代方案缺失→动物研究可能必要→人道对待成为条件
主体三：衣物区别|人造纤维能大规模供应，削弱仅为皮毛杀动物的必要性；肉类产业副产品利用与专为皮毛猎杀分开判断。|替代纤维存在→可以大量生产→专为衣物屠杀无必要→利用现有副产品→禁止专门猎杀
结尾：条件保持一致|结尾允许的是仍有必要的食品和医药用途，禁令只针对专为皮毛的猎杀；避免把正文条件丢掉。|必要性保留→食物医药有条件允许→专为皮毛猎杀应禁止
''', '''
can be morally justified|校|给出道德辩护而非事实解释；N/V-ing + can be morally justified + 条件。|Temporary restrictions on travel can be morally justified when they protect people from an immediate danger.
rely solely on|校|强调唯一依赖对象；rely solely on + N/V-ing，随后应检查有无替代。|Rural schools should not rely solely on unpaid volunteers.
provided that|校|引入必要条件；provided that + 完整从句。|Remote working can be expanded, provided that staff receive adequate technical support.
on a large scale|校|说明实施或生产规模；produce/implement + N + on a large scale。|Affordable learning materials can be distributed on a large scale through online platforms.
strict prohibition on|校|表达严厉禁止；a strict prohibition on + N/V-ing。|A strict prohibition on misleading advertisements could protect vulnerable consumers.
''', '''
为什么不能用“蔬果不能养活全世界”直接支持食用动物？|植物性食品不只蔬果；本文真正保留的条件是营养充分的替代品是否人人可获得。
医药段允许动物研究的两个条件是什么？|已验证替代方法不可用，且研究中的动物受到人道对待。
衣物段怎样区分副产品利用与专门猎杀？|可充分利用肉类产业已经产生的皮革，但有大规模替代品时，不应仅为皮毛猎杀动物。
''', '换成学校使用人工智能：写两句有条件允许，说明何时仍需教师参与。', 'AI tools can assist with routine practice, provided that teachers check their feedback. Schools should not rely solely on automated systems when learners need individual explanations.')

add(3, 'Is Wildlife Conservation Overfunded?', '同意程度题', '不同意保护投入过多；人为损害仍要求保护，预算应兼顾生态与人的需要。', '''
开头：比较投入标准|争论不是动物是否重要，而是现有努力是否超过所需；文章明确判断实际努力仍少于防止灭绝的需要。|保护重要→出现资源过多质疑→现有努力少于所需
主体一：回应自然淘汰说|先把适者生存归给反方，再区分自然灭绝与伐木、扩城、偷猎造成的下降；人为损害提供干预理由。|反方诉诸自然淘汰→当前下降也关联人类活动→栖息地破坏和偷猎加剧风险→需要保护减损
主体二：比较预算机会成本|承认发展中国家有医疗、教育和就业需求，但两类支出并非互斥；小额保护预算转移可能帮助有限，却放任生态损害。|公共预算有多项需求→可兼顾保护与民生→小额转移改善可能有限→生态受损也影响人类
结尾：及时投入|有财政成本不等于应停止保护；面对物种灭绝风险，结尾主张继续行动并增加所需关注。|保护有成本→灭绝风险仍存在→继续及时保护
''', '''
prevent animals from dying out|熟|防止灭绝；prevent + 对象 + from V-ing，die out不及物。|Affordable meals can prevent students from dropping out because of financial pressure.
better-adapted|校|更能适应环境；better-adapted + N，也可be better adapted to + N。|Better-adapted teaching materials can support learners with different needs.
correlate with|校|表达相关而非已证实因果；A correlate with B。|Long commuting times may correlate with lower job satisfaction.
mutually exclusive|校|说明两选项互斥；A and B + be mutually exclusive，否定时表示可以并存。|Economic growth and fair working conditions need not be mutually exclusive.
far-reaching effects on|熟|说明影响范围广或持久；have far-reaching effects on + N。|Unequal access to education can have far-reaching effects on employment opportunities.
''', '''
反方的适者生存论为什么不能直接排除保护？|当前物种下降不只是自然过程，还关联伐木、城市扩张和偷猎等人为损害。
本文怎样限定挪用保护预算的机会成本判断？|只说相对较小的预算可能给其他领域带来有限改善，未断言转移所有保护经费都没有帮助。
mutually exclusive在预算段否定了哪种前提？|否定保护动物与改善人类福祉只能选其一，政府可以同时分配资源。
''', '换成图书馆与医疗预算：承认财政竞争，再说明不能仅因另一领域有需求就取消小额文化支出。', 'Healthcare and public libraries need not be mutually exclusive budget priorities. Transferring a small library budget may bring limited medical improvements while removing a valuable learning service.')

add(4, 'Protect All Wildlife or Selected Species?', '双边讨论＋个人观点题', '所有野生动物都值得免受人为伤害，但可按威胁程度分配不同资源。', '''
开头：提出两种保护范围|区分选择性保护与所有动物都应得到关注，为后文把保护原则和资源分配拆开作铺垫。|保护重要→选择部分物种→广泛保护所有物种→需要明确分配原则
主体一：解释选择性投入|老虎濒危而城市鼠鸽适应良好，支持不同强度投入；蜂类若种群稳定，较低的是紧迫性而非生态价值。|物种威胁不同→濒危者需密集保护→稳定种群紧迫性较低→无需同等投入
主体二：普遍保护的责任|人类伐木、扩城和偷猎使多类物种受威胁，因此不能只按外观或主观价值挑选，必须减少普遍的人为伤害。|人类活动损害多种物种→部分种群下降→应阻止破坏行为→保护不只限于高观赏价值动物
观点段：生态联系与分层措施|蜂类减少可能影响授粉，再影响草食动物和捕食者；关联支持整体保护，但不要求每种动物获同额经费。|蜂类减少→授粉受影响→依赖植物的草食动物受影响→食物链可能波及捕食者→保护广泛而投入有别
结尾：原则与优先级并存|尽量保护更多物种，同时按具体风险优先分配关注和资源；不是先支持全部、最后又取消部分动物资格。|尽量广泛保护→评估物种风险→确定资源优先级
''', '''
be distinguished from|校|区分对象；A should be distinguished from B，情态动词后保留be。|Temporary unemployment should be distinguished from a long-term skills mismatch.
insufficient justification for|校|说明理由不足；there is insufficient justification for + N/V-ing。|There is insufficient justification for banning all online lessons because some are poorly designed.
deserve protection|校|表达应受保护；对象 + deserve protection from + 伤害。|Children deserve protection from misleading commercial messages.
closely interconnected|校|强调相互联系；复数事物 + be closely interconnected，不能据此推出价值相等。|Housing costs and commuting choices are closely interconnected.
according to the threats they face|校|按风险分配；according to + N/名词性结构，they应有明确先行词。|Schools could direct support to learners according to the difficulties they face.
''', '''
种群数量稳定为什么不能推出动物不重要？|数量与生态价值是不同维度；稳定种群只可能降低立即保护的紧迫性。
蜂类例子如何从授粉接到捕食者？|蜂类减少可能损害授粉，进而影响相关植物、依赖这些植物的草食动物，最后可能波及捕食者。
“保护全部”与“部分优先”如何不矛盾？|全部动物都有免受人为伤害的资格，具体投入可以按面临威胁的程度区别安排。
''', '换成教育公平：说明所有学生都有学习机会，但辅导强度可因需要不同而不同。', 'All students deserve access to suitable learning resources. Schools can nevertheless provide different levels of support according to the difficulties learners face.')

add(5, 'Declining Animal and Plant Populations', '原因＋解决措施双问题', '主因是破坏性人类活动；政府修复栖息地，个人拒买非法野生动植物产品。', '''
开头：原因与行动主体|题目问为什么及如何解决；开头同时给出人为破坏与政府、个人共同努力，避免只描述数量下降。|动植物数量下降→破坏性人类活动→政府与个人都需行动
主体一：拆分两类人为压力|农业扩张、伐木和基建直接清理家园；宠物、药材和动物部位的需求推动非法交易，两条机制共同增加灭绝风险。|开发土地→自然栖息地减少→物种失去家园→非法交易需求增加→生存风险上升
主体二：措施对准成因|政府用本土树种重造栖息地，个人从认识伤害转为拒买象牙和非法药材；意识必须落实为减少需求。|重植本土树种→恢复栖息地→识别消费造成的损害→拒买相关非法产品→降低猎杀和采集需求
结尾：统一因果与措施|take a heavy toll on概括人为伤害，再用政策与个人拒买对应两条成因；不把责任只推给政府。|人为活动造成损害→政策修复与个人拒买→缓解生物多样性下降
''', '''
depriving countless species of their natural homes|熟|用分词写结果；deprive + 对象 + of + N，不能写from。|Excessive overtime can deprive workers of their opportunity to rest.
driven by high demand for|熟|说明需求推动行为；be driven by demand for + N。|The expansion of online courses is partly driven by high demand for flexible study.
conservation and restoration efforts|熟|区分保护与修复；efforts to + V，也可将整组作主语。|Maintenance and restoration efforts could make old schools safer to use.
take to halt and reverse the trend|熟|询问具体步骤；take steps to + V，halt停止、reverse扭转。|What steps can employers take to halt and reverse the trend towards longer working hours?
taken a heavy toll on|校|造成严重损害；have/has taken a heavy toll on + N。|Repeated delays have taken a heavy toll on passengers' confidence in the rail service.
''', '''
土地开发和非法交易分别通过什么机制损害物种？|前者清理栖息地使物种失去家园；后者由消费需求推动过量捕猎和采集。
为什么只提高环保意识还不足以完成解决方案？|必须把认识伤害接到拒买非法产品，减少需求才可能减弱猎杀和采集动机。
政府的重新造林怎样对应主体一？|在受毁林地区重植本土树种，为失去家园的物种重新提供适合栖息的空间。
''', '换成食品浪费：政府改善设施，个人改变购买行为，用两句分别对应成因。', 'Local councils can improve food collection facilities to reduce waste from disposal. Individuals can also help by planning meals and avoiding purchases they are unlikely to use.')

add(6, 'Why International Tourism Is Growing', '原因＋正负评价双问题', '收入和廉价航空推动国际旅游；风险受管理时总体积极。', '''
开头：两问同时回答|收入与航空发展回答增长原因，积极评价附带风险管理条件；不是无条件声称游客越多越好。|更多人出国→收入和航空发展→风险受控时总体积极
主体一：支付能力与可达性|中产扩大使更多人有可支配收入；飞机效率、航空竞争和廉航扩展一起降低旅行门槛，构成需求与供给双侧解释。|中产扩大→可支配收入增多→飞机效率与航空竞争提高→廉航扩展→国际旅行更可负担
主体二：文化与经济收益|旅游者亲历饮食节日，目的地从景点吸引的消费获得收入；居民生活改善依赖游客消费进入本地经济。|接触当地饮食节日→获得文化体验→景点吸引游客→游客消费→本地收入可能提高
主体三：环境损害与对应措施|酒店道路开发可毁林并损害栖息地，政府限制开发、个人保护珊瑚等各有作用；具体行动解释风险如何受控。|旅游设施扩张→毁林建设→栖息地与物种受损→政府限制破坏→游客减少直接伤害
结尾：有条件的双赢|重申收入与廉价航空原因，收益判断依靠政策和个人行为控制损害；结尾保留provided that条件。|收入与低价航空推动→旅游者和目的地受益→政策与个人努力控制风险
''', '''
disposable income|熟|可用于储蓄或非基本消费的收入；use disposable income to + V。|Higher disposable income may allow families to buy additional learning materials.
the middle class is expanding|校|描述群体扩大；the middle class + 单数谓语，不写the number...proliferates。|As the local workforce is expanding, demand for reliable public transport may rise.
ranging from|熟|展示范围；ranging from + A + to + B，两端结构应平行。|Students need support ranging from academic advice to affordable accommodation.
concerted efforts from|熟|多方协同行动；concerted efforts from + 主体，须补谁做什么。|Improving school meals requires concerted efforts from teachers and catering staff.
provided that|校|限定积极结论；provided that + 完整条件从句。|Longer opening hours could benefit library users, provided that staffing costs remain manageable.
''', '''
本篇把旅游增长拆成哪两类门槛降低？|收入增长提高支付能力，飞机效率、航空竞争和廉航发展改善可达性与价格。
游客到来怎样可能改善本地生活？|景点吸引游客，游客消费进入本地服务和收入，才可能提高居民生活水平。
政府和游客各做什么来对应环境损害？|政府限制为旅游设施毁林并管理塑料用品；游客采取负责任行为，例如潜水不触碰珊瑚。
''', '换成在线教育增长：解释设备与价格门槛下降，并给积极判断加上质量条件。', 'Affordable devices and wider internet access have made online courses easier to use. This can be a positive development, provided that learners receive reliable content and appropriate feedback.')

add(7, 'Weighing International Tourism', '利弊权衡题（是否弊大于利）', '不同意弊大于利；有效监管限制剩余损害时，就业收入与文化保护的持续收益更大。', '''
开头：直接给权衡答案|用On balance明确总体收益更大，同时承认环境与文化问题，后文须解释为何这些损害不足以压过收益。|国际旅游繁荣→环境文化风险存在→总体经济与文化收益较大
主体一：就业与收入|游客消费创造岗位和外汇，旅游收入可提高人均收入；特别需要岗位的地区受益，但旅游并非唯一发展渠道。|游客进入→岗位与外汇增加→收入可能提高→发展中地区获得就业机会
主体二：环境风险可被限制|设施和基建扩展导致毁林与栖息地损害，监管开发与游客行为可削弱这条链；承认可缓解还不是完整权衡。|设施扩展→毁林建设→栖息地损失→限制开发与减少游客伤害→剩余损害降低
主体三：文化风险可转为保护动力|迎合游客可能商业化传统；若本地人经营旅游并把收入用于习俗，旅游本身可成为文化保护载体。|迎合外来需求→传统可能弱化→政策重视文化→本地社区经营并回投收入→文化认同增强
结尾：比较剩余损害与持续收益|只在保护措施限制损害时支持旅游，比较的是持续生计和文化保存收益与控制后的损害，不是单纯数优点。|监管和各方努力→环境文化损害有限→持续生计与文化收益→收益超过剩余损害
''', '''
earn foreign exchange|校|说明外汇收益；earn + foreign exchange，exchange此义不可数。|Exporting educational software can help small firms earn foreign exchange.
take its toll on|熟|损害某对象；N + take its toll on + N，its指前述事物。|Persistent staff shortages can take their toll on hospital services.
place a premium on|熟|高度重视；place a premium on + N/V-ing。|Employers should place a premium on relevant skills when recruiting graduates.
a vehicle for|熟|把活动视为实现目标的载体；become/serve as a vehicle for + N/V-ing。|Community theatre can serve as a vehicle for discussing local concerns.
heighten a sense of belonging|校|增强归属感；heighten a sense of + N，不表示人数增加。|Inclusive school activities may heighten a sense of belonging among new pupils.
''', '''
为什么删掉旅游机会“only come with”这一说法？|旅游可创造岗位，但没有证据表明所有发展机会只能来自旅游。
文化段中谁被缓解，谁成为保护载体？|负面影响被缓解；旅游本身成为保护和复兴文化的载体，不能让负面影响充当载体。
结尾用什么具体依据判断利大于弊？|监管使环境文化损害有限后，持续的本地生计和文化保存收益超过剩余损害。
''', '换成城市艺术节的利弊：说明社区收入回投与噪声管控，给出有条件权衡。', 'A community arts festival can generate income that residents use to maintain local venues. Where organisers keep noise and waste limited, these continuing cultural benefits may outweigh the remaining disruption.')

add(8, 'Travel and Learning About Culture', '同意程度题', '部分同意媒介能提供文化知识，但不能完全替代旅行的亲身学习与个人体验。', '''
开头：限定替代程度|问题在于媒介能否替代了解文化所需的旅行，而非旅游是否重要；用cannot fully replace保留部分替代的空间。|媒介文化资源增长→有人认为无需旅行→信息可替代一部分→直接体验不可完全替代
主体一：承认媒介优势|书影网络让人在家获取文化信息，节约交通住宿的时间和费用，因此对无需旅行的命题作程度性让步。|旅行耗费时间金钱→媒介在家可访问→获得部分文化信息→节省旅行成本
主体二：文化亲历与附带经济效益|和当地人一起饮食过节带来描述难复现的学习；目的地收入另列为附带收益，不拿经济价值证明学习必要性。|与当地人共同参与习俗→获得直接文化经验→文字描述难完全复现→游客消费另有经济收益
主体三：个人经历不可复制|计划、迷路、误车以及现实与介绍不符，形成旅行者自己的记忆；他人的叙述不能完整替代此种个人经历。|计划旅行→经历意外与现实差异→形成个人理解→留下自己的记忆→媒介无法完整复现
结尾：知识与体验分开|媒介可探索世界，旅行可直接体验并加深理解；结尾不推出只有出行才能理解文化的绝对结论。|媒介提供知识→旅行深化亲历理解→目的地另获经济收益
''', '''
cannot fully replace|校|承认部分替代但否定完全替代；A cannot fully replace B。|Recorded lessons cannot fully replace individual feedback from a teacher.
be it time or money|熟|列出无论哪种资源；resource, be it A or B，正式让步结构。|Every form of support, be it advice or funding, should address a clear need.
in the comfort of their own homes|校|说明在家舒适获取；in the comfort of + 所有格 + own home(s)。|Older patients can speak to a doctor in the comfort of their own homes.
discrepancy between the plan and the reality|熟|比较预期与实际差距；a discrepancy between A and B。|A discrepancy between advertised prices and final charges may damage consumer trust.
cannot fully reproduce|校|不能完整复现体验；媒介 + cannot fully reproduce + N。|A virtual laboratory cannot fully reproduce the experience of handling physical equipment.
''', '''
为什么经济收益不能单独反驳“了解文化无需旅行”？|它证明旅游对目的地有利，却没有证明旅游对文化学习不可替代；需要亲历学习的理由。
主体一承认媒介能实现哪些功能？|人在家获得部分文化知识，并节省本来用于交通住宿的时间和金钱。
个人旅行体验的链条有哪些环节？|做计划，遭遇误车迷路等事件，认识计划与现实差异，形成自己的长期记忆。
''', '换成远程实验教学：承认视频能传递步骤，再说明操作经验的替代边界。', 'Videos can explain laboratory procedures in the comfort of students\' own homes. However, they cannot fully reproduce the practical judgement developed through handling equipment and correcting mistakes.')

add(9, 'The Benefits and Risks of Video Games', '利弊权衡题', '适当内容与适度使用下利大于弊；承认不适当或过量使用的健康和行为风险。', '''
开头：明确收益胜出|开头承认成瘾可能带来身心问题，也呈现学习娱乐功能，直接回答advantages outweigh；后文必须提供适用条件。|游戏受欢迎→成瘾风险与教育娱乐价值并存→总体认为收益更大
主体一：风险具体化|暴力内容可能影响冲突处理观念；过度游戏挤占户外活动形成久坐，并可能干扰其他任务注意力，不能把所有玩家都归为受害者。|不当内容影响暴力观念→过度游戏挤占活动→久坐习惯→可能增加健康与注意力问题
主体二：适度价值与学习边界|适度游戏可暂离压力，操作训练协调和决策；历史背景游戏可引入知识，但虚构内容仍须与史实区分。|控制时长→减轻过量使用风险→暂时放松→练习协调决策→接触历史但辨别虚构
结尾：解释为何收益更大|用选择内容、限制时间和监管自律降低许多风险，使娱乐学习价值保留；权衡结论依赖这些条件。|选择适当内容→限制时长→多类风险减少→娱乐学习收益得以保留
''', '''
susceptible to|熟|容易受某因素影响；be susceptible to + N，to是介词。|Inexperienced consumers may be susceptible to misleading advertising.
cope with interpersonal conflicts|校|处理人际冲突；cope with + N，不直接接宾语。|School mediation programmes can help pupils cope with interpersonal conflicts.
played in moderation|校|适度使用；be played in moderation，也可consume/use N in moderation。|Social media can support communication when used in moderation.
hand-eye coordination|熟|手眼协调；develop/improve + hand-eye coordination。|Practical craft lessons may improve children's hand-eye coordination.
fictional elements need to be distinguished from historical facts|校|区分虚构与事实；A need to be distinguished from B。|In science lessons, tentative explanations need to be distinguished from established findings.
''', '''
健康风险段怎样避免“游戏必然使人近视”的跳跃？|只展开过度游戏减少户外活动并形成久坐的链条，用may保留风险程度，没有推出必然近视。
为什么把责任推给上瘾玩家仍不能证明游戏无害？|责任归属与风险存在是两回事；只有限定适度使用，才可支持有条件的娱乐价值。
历史游戏带来学习收益时还需要什么限制？|可能介绍历史事件人物，但玩家必须区分虚构元素与历史事实。
''', '换成社交媒体的利弊：用适度使用保留沟通收益，说明限制时间如何减少成本。', 'Social media can help distant relatives remain in contact when used in moderation. Limiting daily use may reduce time lost to repetitive browsing while preserving this communication benefit.')

add(10, 'Why Adults Choose Mobile Games', '原因＋正负评价双问题', '便捷、便宜及社交娱乐推动手游；习惯性或过度游戏挤占活动时总体负面。', '''
开头：原因与评价|先用随时可接触性解释增长，再提出成瘾和浪费时间的风险；负面评价须结合后文的过度使用条件理解。|成人空闲玩手游增多→随手可得→娱乐有价值→过度使用可能损害时间安排
主体一：设备与成本优势|手机让游戏脱离电脑和主机，通勤等碎片时间也能玩；比钓鱼爬山更省准备、时间和金钱，并能与玩家交流。|手机可随身携带→任何地点短时游戏→时间金钱门槛较低→放松打发时间并社交
主体二：奖励机制与机会成本|部分手游的重复任务和每日奖励延长参与；当它们挤占睡眠、运动、家人和其他兴趣，才产生明确损失，不借简化生理解释代替机制。|重复任务与频繁奖励→长时间占用与每日登录→睡眠运动被挤占→陪伴与其他爱好机会减少
结尾：限制评价范围|重申技术便利和低价娱乐原因，批评的是习惯性游戏替代更积极用途的情形，因此提出适度使用而非全面停止。|便利与廉价推动→习惯游戏挤占其他活动→负面时间成本→适度游戏并重新分配时间
''', '''
ready accessibility|校|随时容易接触；the ready accessibility of + N，区别有没有与负担得起。|The ready accessibility of online dictionaries can support independent reading.
switch off from the pressures of real life|熟|暂时摆脱压力；switch off from + N，不等于解决压力根源。|A short walk can help employees switch off from the pressures of work.
keep users occupied|校|使人持续投入；keep + 对象 + 形容词或分词，不写keep sb to do。|Interactive museum exhibits can keep visitors occupied while they wait for a tour.
could otherwise be spent with|校|表达时间的替代用途；time + that could otherwise be spent with + 人。|Long commutes consume time that could otherwise be spent with children.
pursue other hobbies|校|主动发展其他兴趣；pursue + hobby/interest，不必加介词。|A shorter working week may give employees time to pursue other hobbies.
''', '''
手游的便利除了价格低还包括什么？|手机随身可用，通勤或等待时能玩，不需要电脑主机或户外活动的准备。
奖励机制怎样接到健康风险，中间不能省哪一步？|频繁奖励与每日登录延长游戏时间，只有当时间挤占睡眠和运动时，才说明可能损害健康。
为什么用other hobbies而不是暗示游戏不是爱好？|游戏本身可以是爱好；文章批评过度游戏减少其他兴趣和家庭时间。
''', '换成短视频：写便利原因，再以睡眠和家庭时间说明过度使用的机会成本。', 'Short videos are readily available on smartphones, making them easy to watch during brief breaks. Excessive viewing may nevertheless consume time that could otherwise be spent with family members or used for sleep.')

add(11, 'Censorship of Violent Entertainment', '双边讨论＋个人观点题', '大部分暴力娱乐可以保留，兼顾内容的反思价值，并限制极端场面、保护年轻观众。', '''
开头：准确列出双方|一方担忧社会影响并主张审查，另一方视为无害放松；后文应检验风险与价值，不把所有娱乐自动归为同类。|暴力娱乐流行→一方担忧社会影响→另一方强调放松→需要平衡判断
主体一：模仿风险|部分年轻人难分虚构与现实，可能把作品中的暴力当作应对冲突的方法；假设模仿情景说明可能性，不冒充实际犯罪证据。|部分年轻人辨别困难→受暴力内容影响→把威胁当作处理冲突方法→现实冲突可能恶化
主体二：反对草率归因|许多人能区分虚构，享受替代性刺激并不直接证明愿意现实施暴；社会问题有多种背景，外观相似不足以确定因果。|观众可分虚构现实→娱乐刺激不等于施暴意愿→社会问题有多重因素→不能仅凭相似行为归因
观点段：教育效果的内容条件|呈现暴力后果可能引发共情、反思和敬佩勇气；只有特定内容、部分观众才支持可能的劝阻效果。|看到暴力后果→理解受害伤害→共情与反思→部分观众可能打消施暴念头
结尾：允许与限制并行|允许放松和教育价值存在的内容，同时针对极端场景及年轻观众施加限制；不是一概审查或无条件开放。|风险因人和内容而异→多数内容可允许→限制极端场景→保护年轻观众
''', '''
distinguishing between the virtual world and reality|校|区分两对象；have difficulty distinguishing between A and B，difficulty后接V-ing。|Some consumers have difficulty distinguishing between reliable advice and paid promotion.
cope with interpersonal conflicts|熟|处理人际冲突；cope with + N。|Workplace training can teach staff to cope with interpersonal conflicts through discussion.
experiencing a vicarious thrill|熟|通过他人经历获得刺激；experience a vicarious thrill，不推出实际行为意愿。|Reading an adventure novel can give pupils a vicarious thrill without exposing them to danger.
dissuaded from such behaviour|校|劝阻某种行为；be dissuaded from + N/V-ing。|Drivers may be dissuaded from speeding when they understand the risks to pedestrians.
impose appropriate restrictions on|校|施加针对性限制；impose restrictions on + 内容或行为。|Schools may impose appropriate restrictions on phone use during lessons.
''', '''
“不是犯罪的必要条件”为什么不能证明暴力娱乐无害？|不是必要条件只说明没有它也能犯罪，不能排除某些内容对某些人的影响。
本篇如何限定观看暴力内容的教育效果？|限定为呈现暴力后果的内容，对部分人可能产生理解、共情和反思，而非多数人必然被劝阻。
作者允许大部分内容时保留哪些监管？|对极端暴力场景施加适当限制，并保护年轻观众。
''', '换成社交媒体谣言监管：承认使用价值，解释针对性限制而非全面禁止。', 'Social media can help residents exchange useful local information. Platforms should nevertheless impose appropriate restrictions on demonstrably misleading content that may expose vulnerable users to harm.')

add(12, 'Women in Policing and the Military', '双边讨论＋个人观点题', '支持女性参与；以具体职责和个人能力判断适岗，而非以性别整体排除。', '''
开头：争议与群体印象|呈现体能差异论和女性同样能胜任论，后文用岗位内容与个体能力检验，不把平均差异直接变成每个人结论。|体能差异认知→有人反对女性入职→有人支持能力平等→检验岗位与个人
主体一：承认高体能门槛|值勤、轮班和面对危险确有体能心理要求，但不达标者不适合特定任务的结论对所有性别适用。|具体职责体能要求高→需通过体测并应对危险→按相关标准筛选→不达标不适合该任务
主体二：警务职责多样|社区警务不只依赖力量，还需判断、沟通及亲和；具备这些能力的女性可改善警民关系，避免说所有女性天生更善沟通。|日常警务服务社区→访谈巡逻调查需判断沟通→具备能力的女性可胜任→促进警民联系
主体三：军务超出战斗|士兵并非总从事战斗，装备可能缩小部分体能差距，战术策略也影响成败；性别不决定个人智力。|军事岗位不全是战斗→装备改变部分体能要求→战术策略也重要→女性可在多军种贡献
结尾：能力与参与统一|承认平均体能差异，同时重申职责范围广且依赖不同个人能力，因此女性有能力参与且已经参与。|平均差异可能存在→岗位需要多种能力→女性能参与且已参与
''', '''
ill-equipped to work|熟|缺乏任职准备或条件；be ill-equipped to + V，应以实际能力证明。|Schools without reliable internet may be ill-equipped to work with digital teaching platforms.
regardless of gender|校|排除性别作为筛选依据；regardless of + N。|All applicants should receive the same assessment regardless of age.
rely on judgement and communication|校|说明任务依赖能力；rely on + N/V-ing。|Effective customer support may rely on judgement and communication as well as technical knowledge.
rests not only on|校|列出不止一个基础；X rests not only on A but also on B，结构平行。|Successful language learning rests not only on memory but also on regular practice.
a central role in|熟|参与的关键作用；play a central role in + N/V-ing；正文的play被插入语隔开。|Parents can play a central role in helping children develop healthy reading habits.
''', '''
岗位体能要求为什么不能证明女性整体不适合？|只能说明未达到相关标准的个人不适合特定职责，性别不能替代个体能力评估。
社区警务段列出哪些不只靠力量的能力？|判断、沟通、亲和和同理；这些能力用于访谈、巡逻、交通调查及建立警民关系。
军事段如何支持女性参与又避免否认战斗存在？|承认士兵并非总执行战斗任务，装备可能缩小部分差距，策略能力也重要，不说现代军人不再作战。
''', '换成年长员工招聘：承认部分岗位要求，再用个人能力标准避免年龄整体排除。', 'Some technical jobs require staff to learn new systems quickly. Employers should assess each applicant against these requirements rather than assume that older workers are ill-equipped to meet them.')

add(13, 'Fathers as Stay-at-Home Parents', '原因＋正负评价双问题', '女性收入机会与男性成功观念变化促成父亲留家；双方工作和照护选择更多，总体积极。', '''
开头：变化程度与两问|传统分工是在许多家庭中改变，并非已经消失；开头指出职场歧视减轻和男性成功标准变化，再明确积极评价。|传统分工改变→女性机会增多→男性成功标准变化→总体积极
主体一：补足家庭收入比较|女性获得高薪专业与就业机会提高挣钱能力；只有接上母亲收入前景优于伴侣，才能解释为什么父亲选择留家。|教育就业障碍减少→更多女性进入高薪职业→母亲收入前景更强→母亲工作更合算→父亲承担照护
主体二：育儿选择获得尊重|成功不再只按事业和物质衡量，父亲育儿更可能得到尊重，降低羞耻和被批评的顾虑；No longer should是规范主张而非现实已无偏见。|成功标准不只限事业→社会更尊重个人选择→父亲育儿顾虑减轻→更能自信承担照护
结尾：评价依据|积极性来自男女均可选择有偿工作与育儿分工，属于机会与自主权扩大，不是简单把传统角色互换。|有偿工作与照护自由扩大→男女自主权提高→平等取得进步
''', '''
breadwinners|熟|家庭主要收入提供者；be/become breadwinners，勿与所有就业者混同。|Flexible training can help unemployed parents become breadwinners again.
make financial sense|校|从财务上合理；it makes financial sense for + 人 + to V。|It may make financial sense for a small company to rent shared office space.
earning prospects|校|未来收入机会；have stronger/better earning prospects than + 比较对象。|Graduates with practical experience may have better earning prospects than equally qualified applicants without it.
family-oriented|熟|重视家庭；be family-oriented或a family-oriented + N，不代表缺乏事业投入。|Family-oriented workplace policies may improve staff retention.
freedom of choice|熟|选择自主权；freedom of choice over + N，本文涉及工作与照护。|Students need freedom of choice over optional subjects.
''', '''
女性能够成为养家者与父亲留家之间缺哪一步？|比较家庭双方收入前景；当母亲更有挣钱优势时，让父亲照护可能更合算。
男性成功标准变化如何影响育儿选择？|社会不只用事业与物质评价男性，更尊重父亲的偏好，使留家育儿更容易获得认可。
本文为什么认为趋势积极，而非只描述分工改变？|男女都得到更多决定工作与育儿安排的自由，机会和自主权扩大。
''', '换成伴侣一方转为远程工作：说明收入与家庭安排共同决定选择，不按性别预设。', 'When one partner has stronger earning prospects, it may make financial sense for the other to choose flexible work. The decision should reflect the household\'s needs and both partners\' preferences.')

add(14, 'Equal University Admissions by Gender', '同意程度题', '反对所有专业一律男女等额；应尊重选择、按相关学术标准录取并去除歧视障碍。', '''
开头：反对一刀切|平等配额看似代表改善，但文章反对每个专业统一强制；判断对象是普遍要求，不是否认促进平等的目标。|促进性别平等→提出各专业等额→表面体现平等→一刀切可能反效果
主体一：先解释政策吸引力|性别刻板印象使女生被导向特定专业，配额可增加工程等男性主导专业的女生名额，因而看似改善机会。|刻板印象限制专业选择→工程等专业男性占多→配额增加女生名额→看似推进平等
主体二：名额限制机制|合格申请者可能仅因比例目标被拒，男女均可能失去偏好专业名额；配额不是必然强制分配专业。|固定男女比例→合格申请者因性别被拒→偏好专业机会减少→个人发展选择受限
主体三：人数差与机会差区分|个人偏好和歧视可共同影响申请；有数量差不能单独证明机会不平等，也不能据此否认存在歧视。|个人偏好与歧视并存→专业申请人数可能不同→人数差本身不足证明机会差
结尾：提出替代原则|保留自由选择并去掉歧视障碍，再按相关学术要求评估；不是把现状全部合理化。|保护学生选择→去除歧视障碍→不以每个人数差强行配额
''', '''
as a blanket requirement|校|指不分情况的统一要求；impose/introduce N as a blanket requirement。|Daily office attendance may be unnecessary as a blanket requirement for all staff.
denied places|校|被拒绝录取名额；be denied places in + 专业或机构。|Qualified rural applicants may be denied places if interviews are only held in distant cities.
freedom of choice|熟|自由选择；protect/restrict freedom of choice，说明选择对象。|A wider range of bus routes can increase commuters' freedom of choice.
preferences for|校|对某对象的偏好；preferences for + N/V-ing，不用towards。|People's preferences for working hours may change after they become parents.
not in itself evidence of|校|单一现象不足证明结论；A is not in itself evidence of B。|A low price is not in itself evidence of poor product quality.
''', '''
配额可能怎样限制选择，为什么不写成强制分科？|合格申请者可能因比例要求被拒绝偏好专业名额，但配额不必然把他们直接分配去另一专业。
本篇为什么把not discrimination but preference改成alongside？|歧视和偏好可以同时影响选择，没有依据把两者排成非此即彼。
反对等额后应提出哪两个兼容原则？|保护学生选择自由，同时消除歧视障碍，并按相关学术标准录取。
''', '换成城市公共设施规划：说明人数差不能直接证明机会差，要求检查参与障碍。', 'Unequal attendance at two community centres is not in itself evidence of unequal opportunity. Planners should examine residents\' preferences while removing transport and access barriers.')

add(15, 'Equal Numbers in the Workplace', '正负发展评价题', '仅依赖人数相等是负面发展；它虽增机会，但可能掩盖薪资、晋升与照护障碍。', '''
开头：锁定依赖人数的风险|等额招聘表面体现平等，但文章评价的是把人数当成完成平等工作的充分证据，负面判断由此成立。|企业推行等额招聘→表面平等→可能掩盖持续不平等→依赖人数达标有负面效果
主体一：承认招聘收益|刻板印象使一些雇主更偏好男性，等额政策可提高女性进入工程、外科等领域的机会；先公平解释正方。|刻板印象影响招聘→雇主偏好男性→等额政策增加女候选人机会→更多进入原男性主导职业
主体二：数量不足与条件反效果|真正平等涉及同值同酬、参与、领导和照护责任；若企业以人数达标替代进一步行动，薪资晋升障碍可能继续。|人数相等不涵盖待遇机会→薪资晋升照护障碍仍在→企业以达标宣称已尽责→后续改革减少→隐藏不平等持续
结尾：结论保持限定|不否认岗位机会增加，但反对把等额视为充分措施；要求继续减少实际障碍。|承认招聘收益→等额不充分→继续处理实际不平等
''', '''
in favour of this equal-number policy|校|引出政策支持理由；the argument in favour of + N/V-ing。|The argument in favour of free school meals is that every child can eat during the school day.
place a premium on|熟|高度重视或偏向；place a premium on + N。|Recruiters should place a premium on demonstrated competence rather than familiar university names.
access to these professions|校|进入职业的机会；improve/provide access to + N，access不可数。|Affordable apprenticeships can improve access to skilled professions.
barriers to the full and equal participation|熟|阻碍充分平等参与；barriers to + N/V-ing，to是介词。|Unreliable transport can create barriers to the full and equal participation of rural students.
discrimination related to|校|明确歧视涉及何事；discrimination related to + N，不用松散about。|Recruitment rules should address discrimination related to age and disability.
''', '''
人数相等为什么不足以证明工作场所平等？|仍需检查同值同酬、充分参与、晋升领导机会以及与照护责任相关的歧视。
等额政策在什么条件下可能适得其反？|企业把达标当作已完成平等工作，转移对其他障碍的关注并减少进一步行动。
主体一怎样解释政策可能增加女性机会？|它可抵消部分雇主偏好男性的招聘倾向，让女性更多进入原男性主导职业。
''', '换成学校数字设备公平：说明发放同样数量设备仍可能掩盖使用条件差异。', 'Giving every pupil a tablet can improve access to learning materials. Treating equal device numbers as sufficient may nevertheless hide differences in internet access and adult support at home.')

add(16, 'Is Music a Universal Language?', '同意程度题', '部分同意跨文化情绪交流；不同意音乐能普遍、可靠地传递精确含义。', '''
开头：拆开通用的含义|承认音乐能传递感受，限制的是无需共同背景也能传递具体意义的普遍性；避免把语言资格要求设成绝不含糊。|音乐可传达感受→听众解释多样→精确意义不完全通用
主体一：跨文化情绪共鸣|不逐字分析也能感知温柔或欢快旋律的情绪，不同背景者可能共鸣；may避免声称所有听众反应一致。|不需逐字理解→感知旋律情绪→跨背景听众可能共鸣→解释通用语言称谓
主体二：精确信息受背景限制|歌词隐喻及中西音乐传统需教育、历史与文化背景；同曲不同解说明音乐不可靠地传递精确思想，同时承认口头语言也会含糊。|生活教育经验不同→对歌词背景和惯例理解不同→隐喻及文化联想可能丢失→精确信息交流受限
结尾：保留情绪价值|音乐可以跨越口语连接情感，但没有 universally shared 的精确意义体系；结论不是说音乐无交流功能。|情绪交流跨语言→可连接人群→精确含义缺乏普遍共享体系
''', '''
without a language barrier|熟|无需跨越语言障碍；communicate/appreciate N without a language barrier。|Clear diagrams can help visitors understand safety instructions without a language barrier.
resonate emotionally with|校|与听众情绪共鸣；N may resonate emotionally with + 人。|A documentary about family separation may resonate emotionally with migrant workers.
convey information accurately|熟|准确传递信息；convey + information + accurately，不与定义混淆。|Public transport signs should convey information accurately to unfamiliar passengers.
exchange precise ideas|校|交换精确思想；exchange + N，通常需共同语境。|Shared terminology helps engineers exchange precise ideas during a complex project.
goes beyond spoken language|校|超出口语表达；N goes beyond + N，关系从句须有谓语。|A learner's confidence goes beyond spoken language and may affect classroom participation.
''', '''
本文把“通用语言”分成哪两种交流能力？|跨文化传递某些情绪，与不需共享背景也能可靠传递精确含义。
歌词背景例子怎样显示精确信息的局限？|一人只懂歌词字面，熟悉历史者却识别社会运动隐喻；理解依赖共同背景。
为什么要承认verbal language can also be ambiguous？|避免用所有语言都做不到的绝无歧义标准排除音乐，再比较音乐精确传意的实际局限。
''', '换成公共信息图标：说明直观图像的跨语言优势与精确规则需要文字的边界。', 'Simple icons can convey basic warnings without a language barrier. However, unfamiliar visitors may still need written explanations to understand precise rules and exceptions.')

add(17, 'Music and Everyday Relaxation', '同意程度题（最重要功能）', '同意放松是最重要的日常功能；依据是反复、广泛改善日常身心状态，而非只有放松有价值。', '''
开头：明确比较范围|承认音乐有多种用途，支持的是日常生活中的放松居首；把everyday life作为后文权衡边界。|音乐用途多样→比较日常主要功能→放松最重要
主体一：跨场景放松|通勤、学习后和家务时的情景展示音乐暂离噪声或烦恼的作用，同一功能反复服务工作、学习和家庭生活。|通勤噪声或学习烦恼→音乐暂时转移注意→家务背景音乐→多场景日常减压
主体二：承认其他用途并按标准比较|悲伤音乐也可能安慰，歌曲可助记、鼓舞和传文化；按持续日常福祉贡献比较，放松的广泛重复收益超过部分场合的较窄用途。|情绪安慰与教育文化功能存在→明确日常福祉标准→放松跨生活场景反复受益→部分仪式教育用途较特定
结尾：主要不等于唯一|以最重要日常功能重申立场，同时承认个人放松形式不同；不能因另一功能存在就推翻主要功能。|放松形式因人而异→共享日常减压需求→仍为最重要日常功能
''', '''
take their minds off|熟|暂时不想烦恼；take + 人的mind(s) + off + N。|An outdoor break can take students' minds off a difficult assignment.
in the background|校|作为背景播放；play music/audio in the background。|A recorded announcement may be difficult to hear when other audio is playing in the background.
lift their spirits|熟|振奋情绪；lift + 人的spirits，spirits用复数。|Encouraging feedback can lift employees' spirits after a demanding week.
bring comfort and enjoyment|校|带来安慰愉悦；bring + N + to + 人，勿机械用trigger。|A familiar public garden can bring comfort and enjoyment to older residents.
judged by their contribution to everyday well-being|校|明确评价标准；judged by + N，contribution to + N/V-ing。|Judged by their contribution to community well-being, affordable bus services may deserve priority.
''', '''
存在教育和文化用途是否自动否定放松最重要？|不能；必须按相关标准比较各功能，而非只证明其他功能存在。
本篇采用什么重要性标准，怎样比较？|以对日常身心状态的贡献为准；放松跨工作学习家庭反复受益，部分仪式教育用途范围与场合较窄。
not only...but also中的两个动词为什么分别用trigger与bring？|trigger自然搭配pain/sadness，comfort/enjoyment更自然用bring，不必把优化夸成原句绝对缺谓语。
''', '换成公共公园的主要用途：承认活动与文化价值，再按日常福祉贡献比较休闲功能。', 'Public parks can host cultural events, but their contribution to everyday well-being also matters. Regular opportunities to walk and relax may benefit residents more consistently than occasional ceremonies.')

add(18, 'Public Funding for Health and Education', '双边讨论＋个人观点题', '政府资助基本教育医疗，同时允许愿意者购买额外私人服务。', '''
开头：公平呈现财政分歧|双方分别主张政府出资与个人承担，论题是预算分配及责任，而非先预设私人服务必须被禁止。|公共预算如何分配→政府支付→个人支付→需要比较公共与个人收益
主体一：责任与能力分别论证|教育劳动力和可及医疗使社会整体受益，支持政府责任；税收提供出资能力，两条理由不能互相替代。|教育医疗产生社会收益→政府应资助→税收提供能力→建设公共学校医院
主体二：个人付费与选择担忧|反方担心使用不同却共同付费，另担心公费供给排除付费选择；后一风险以if限定，不能把所有公共保障等同禁私人服务。|个人使用程度不同→反方质疑共同出资公平→若公共供给排除额外服务→愿付费者选择受限
观点结尾：基本保障加私人选择|基本服务关系国家持续发展，应给每个人平等机会；在此基础上允许额外购买，兼顾公共责任与个人意愿。|政府补贴基本服务→全民基本可及→允许私人额外选择→公共与个人努力并存
''', '''
shoulder such responsibilities|熟|承担前述职责；shoulder responsibility for + N/V-ing。|Employers should shoulder responsibility for maintaining safe working conditions.
provide funding|校|提供经费；provide funding to + V / for + N，不写pay for the money。|Councils could provide funding to repair unsafe pedestrian crossings.
have the capacity to do so|校|表达执行能力；have the capacity to + V，do so回指前一动作。|Small schools may wish to offer specialist courses but lack the capacity to do so.
seek a compromise between|熟|在两方间找折中；seek a compromise between A and B。|Transport planners should seek a compromise between faster journeys and quieter neighbourhoods.
equal access to basic services|校|基本服务平等可及；have/ensure equal access to + N，access不可数。|Digital reform should preserve equal access to basic services for people without smartphones.
''', '''
政府应该资助与有能力资助分别用什么理由？|社会受益支持责任；税收资源支持财政能力，不能只用一条代替两项判断。
反方关于私人选择的担忧为何要加if？|只有公共供给排除付费替代时选择才被限制，公费保障本身不必禁止私人服务。
折中方案如何使基本公平与私人选择并存？|政府补贴学校医院确保基本服务平等可及，同时允许愿意付费者购买额外服务。
''', '换成公共交通：写基本服务公共保障与额外私人选择并存的两句方案。', 'Cities should provide funding for reliable basic bus services so that residents can reach work and education. They can also allow private operators to offer additional services for passengers willing to pay more.')

add(19, 'Government Support for Low-Income Students', '同意程度题', '同意政府承担部分责任；预算有限时不必全额支付，可在公共成本可控时提供无息贷款。', '''
开头：责任范围与财政范围|支持帮助贫困生，但反对预算紧张时必须全额承担学费；用some responsibility与in full区分资助职责和支付方式。|贫困生需要支持→政府承担部分责任→有限预算难全额支付→需要折中
主体一：社会回报与财政基础|受教育劳动力服务社会，贫困生未来可能成为专业人才；税收与已有教育预算提供支持能力，但尚未证明能覆盖全部费用。|贫困生完成高教→未来贡献专业能力→政府有公共责任→税收与预算支持一定资助
主体二：预算优先与贷款回收|基础教育已占用预算并可能优先，故以可偿还贷款代替全额拨款；毕业还款可回收部分资金，但无息贷款仍有成本。|基础教育优先占用预算→全额大学资助压力较大→提供助学贷款→毕业后偿还→部分资金回收但仍有公共成本
结尾：贷款的可行条件|重申反对的对象是有限预算下全额支付，并以公共成本可管理为无息贷款的条件；不能一面否定所有financial aid一面支持贷款。|预算有限→全额支付可能不现实→无息贷款提高可及性→成本须可管理
''', '''
shoulder some responsibility|校|承担部分责任；shoulder responsibility for + N/V-ing，some不表示唯一。|Technology firms should shoulder some responsibility for helping users identify misleading content.
financially viable|熟|财务上可行；be financially viable，须比较成本与可用资源。|A new theatre may attract audiences but must also be financially viable.
laying the groundwork for|校|为后续发展打基础；lay the groundwork for + N/V-ing。|Early reading practice can lay the groundwork for independent learning.
full grants|校|全额资助金；provide full grants to + 人 / for + N，grants区别于需还款loans。|A council could provide full grants for essential repairs in low-income households.
public funding can later be recovered|校|说明资金回收可能；funding + can be recovered，不推出零成本。|If the project earns fees, some public funding can later be recovered.
''', '''
“政府有资助责任”为什么不等于“应付清全部学费”？|责任可通过多种支持方式履行，税收资源与社会收益仍不足以证明有限预算能覆盖全部费用。
贷款折中如何缓解永久性支出，又为什么不是零成本？|学生毕业偿还可回收部分资金，但政府仍承担提供和管理贷款的公共成本。
为什么把financial aid is impractical改为paying...in full may be impractical？|financial aid也包含贷款；只限定全额支付才能与后文支持贷款保持一致。
''', '换成政府帮助小企业节能改造：区分全额拨款与可回收贷款，保留公共成本条件。', 'Governments can support small firms that cannot afford energy-saving equipment. Where full grants are too costly, low-interest loans may improve access while allowing some public funding to be recovered.')

add(20, 'Government Responsibility for Childhood Obesity', '同意程度题（责任命题）', '同意政府有责任；成功也需要父母配合，题目未要求政府独自解决。', '''
开头：同意再补充主体|先直接同意政府责任，再以although补充共同努力；父母也有作用不能当作反对政府应负责的理由。|儿童肥胖令人担忧→政府有责任→明确同意→成功仍需父母配合
主体一：责任与政策权力|儿童健康关系社会未来，政府因此有职责；监管面向儿童的不健康食品广告，可通过减弱不良饮食诱导缓解问题。|儿童健康关系未来→政府应承担责任→制定执行广告限制→减少不健康饮食诱导→帮助缓解肥胖
主体二：家庭层面的能力边界|宏观广告监管难直接改变居家久坐，屏幕活动可挤占运动；父母指导才补上政府触及有限的生活习惯环节。|政府能限制广告→居家久坐仍难单独改变→屏幕使用挤占运动→父母指导理解风险→改变不健康选择
结尾：两方责任相容|政府责任仍然成立，父母作用用于解释解决条件；共同创造发展环境，不把共同责任写成取消政府责任。|政府负责宏观环境→父母指导日常习惯→共同支持儿童健康发展
''', '''
take responsibility for|熟|承担某事责任；take responsibility for + N/V-ing，不等于only负责。|Schools should take responsibility for keeping play areas safe.
concerted efforts by|校|说明由谁合作行动；concerted efforts by + 复数主体。|Reducing traffic around schools requires concerted efforts by councils and families.
introduce and enforce laws|校|区分立法与执法；introduce and enforce + laws，不把enforce当颁布。|Authorities can introduce and enforce laws against deceptive financial advertising.
time that could otherwise be spent on|校|时间机会成本；time that could otherwise be spent on + N/V-ing。|Unnecessary meetings consume time that could otherwise be spent on preparing lessons.
an environment conducive to|熟|创造有利环境；an environment conducive to + N/V-ing，to是介词。|Quiet libraries offer an environment conducive to independent study.
''', '''
父母也有责任为什么不反驳原题？|原题问政府是否有责任，未写only；政府有责任与父母配合可以同时成立。
食品广告监管通过什么中间步骤回应肥胖？|广告可能鼓励不健康饮食并增加肥胖风险，限制面向儿童的广告可削弱这条影响。
父母怎样补足政府的能力边界？|政府难直接改变家中久坐，父母可指导孩子理解风险并减少挤占运动的屏幕习惯。
''', '换成网络安全教育：明确学校责任，再用家庭实践补充，不写成反对学校负责。', 'Schools should take responsibility for teaching children how to recognise online risks. Parents can reinforce these lessons at home by discussing suspicious messages and supervising unfamiliar services.')

add(21, 'Teaching Competition and Cooperation', '双边讨论＋个人观点题', '竞争提供个人动力，合作突破个人能力限制；儿童教育应结合两者。', '''
开头：两种教育方向|一方强调竞争意识，另一方强调合作；题目关心未来成为有用成年人，后文应把儿童训练接到成年表现。|儿童教育目标→竞争意识培养→合作技能培养→比较未来社会作用
主体一：竞争激励成长|在竞争情境中较好表现更易获优先，激励学业努力；学习应对挑战可迁移到工作，但不说成绩决定全部机会。|竞争时较好表现获优先→激励追求卓越→学会面对挑战→可能获得更多职业机会
主体二：合作处理复杂任务|公司各部门相互依赖，分享意见还需处理分歧和协商方案；儿童练习这些技能，才可在未来有效团队工作。|复杂问题超出个人→部门协同→分享意见→分歧时达成折中→共同寻求较优方案
观点结尾：功能互补|竞争不足可能减动力，合作不足限制走远；结合个人进步与团队成果，而非抽象说两个都好。|竞争促个人目标→合作补能力限制→融合两者→提高个人与团队成就
''', '''
acts as a catalyst for|校|促成某进展；act as a catalyst for + N/V-ing，不表示唯一原因。|Affordable childcare can act as a catalyst for wider participation in employment.
strive for excellence|熟|努力追求卓越；strive for + N，也可strive to + V。|Regular feedback can encourage trainees to strive for excellence.
rests on the efforts of|校|说明成果依赖多方；X rests on the efforts of + 人或团队。|The success of a public festival rests on the efforts of volunteers and local organisers.
reach a compromise|校|达成折中；reach a compromise when + 完整从句，勿用comprise。|Residents and developers may reach a compromise when their priorities differ.
well equipped for their future lives|校|为未来做好准备；be well equipped for + N / to + V。|Practical budgeting lessons can leave school leavers well equipped for independent life.
''', '''
竞争段如何从学校表现接到成年社会作用？|竞争激励努力与追求卓越，训练应对挑战的能力，未来可能改善工作机会和职业发展。
合作段中分享意见之后还缺哪两步？|意见不同时达成折中，再共同寻找较优方案，不能只用share ideas代替协作全过程。
为什么两者需要结合，而非选出一个普遍胜者？|竞争可提供个人动力，合作可突破个人能力局限；它们分别回应不同障碍。
''', '换成公司绩效制度：用个人激励与跨团队协作各自解决的障碍写两句。', 'Individual targets can encourage employees to strive for excellence. Shared projects are also necessary when solving a problem rests on the efforts of several departments.')

add(22, 'International Cooperation and Local Action', '同意程度题（most与only限定）', '部分同意：跨国问题需协调，但某些紧急区域问题可以独立处理，重要性取决于问题尺度。', '''
开头：明确部分同意范围|many与most不能混为一谈，only又是排他命题；承认许多全球问题需合作，同时保留区域问题可独立解决的范围。|全球问题紧迫→有人主张多数问题仅靠国际合作→全球问题常需协调→部分区域问题可独立处理
主体一：共同责任与协调必要|气候问题由跨国活动形成，国家按贡献程度承担责任；不同收入国家可分工减排和限制毁林，协调提高共同措施效果。|各国共同贡献全球问题→承担程度不同的责任→跨国协调政策→各国分工减排与遏制毁林→共同措施更有效
主体二：因地制宜与独立行动|车少地区换电车即时效果可能有限，需调整重点；塑料堵排水的紧急本地问题可以不等协议就限袋、收垃圾，真正回应only。|国情不同→统一措施即时效果有别→塑料堵塞本地排水→独立限袋与改善收集→无需等待国际协议
结尾：尺度决定分工|国际合作提供全球框架，本地既执行协议也独立处理区域问题；一个本地例子只支持保留范围，不能自动证明多数问题不需合作。|全球挑战需要合作→本地落实具体措施→部分区域问题独立处理→相对重要性随尺度变化
''', '''
So interconnected is the world that|校|强调程度的倒装；So + 形容词 + be + 主语 + that + 完整结果句，that前不加逗号。|So limited is the school budget that essential repairs must be prioritised.
responsibility for mitigating|校|承担减轻某问题的责任；responsibility for + V-ing。|Employers share responsibility for mitigating workplace stress.
albeit to varying degrees|熟|承认程度不同；完整判断后接albeit + 短语，勿另当主句。|Rising housing costs affect many households, albeit to varying degrees.
limited immediate effects|校|限定短期效果；have limited immediate effects on + N，不等于不可行。|New cycling lanes may have limited immediate effects where few residents own bicycles.
without waiting for an international agreement|校|突出可独立行动；without + V-ing，wait for + N。|A town can repair unsafe crossings without waiting for a national transport reform.
''', '''
本地执行国际协议为何还不足以反驳only？|执行仍可能以国际合作为前提；必须提供无需协议也能独立解决的问题与行动。
塑料例子怎样构成独立本地行动？|当垃圾堵塞排水增加洪水风险，本地政府可立即限塑并改善收集，无需等待国际协议。
一个区域反例能否直接推翻“多数紧急问题”需要合作？|不能；它支持限定部分同意的范围，不能单凭一个例子得出多数问题均可独立解决。
''', '换成学校联盟与校内问题：承认共享课程需要合作，但具体安全隐患可由学校独立处理。', 'Schools can cooperate to develop specialist courses that no single school can afford. However, an unsafe staircase can be repaired locally without waiting for an agreement across the entire network.')

add(23, 'Hosting International Sports Events', '双边讨论＋个人观点题', '有条件支持办赛：预期经济文化收益足以支持成本，且财务风险得到管理。', '''
开头：办赛收益与成本之争|问题是主办重大国际赛事的整体效果；引言公平呈现利多与弊多两方，后文把总体判断落实为条件支持。|赛事重要性上升→主办有收益→也有重大成本→需整体评估
主体一：建设开支与债务|赢得主办权后场馆、交通和配套设施耗资，若建造成本超预算可引发债务；投入不是自动形成可回收资产。|获得主办权→建设场馆交通配套→大量资源投入→成本超预算→可能出现债务
主体二：国家地位与文化交流|投入和组织国际活动可提升地位；赛事展示文化，参与者学习其他文化，动作主体必须分清。|承担国际组织责任→展现国家与文化→参与者学习他国文化→促进理解合作
观点段：收入缓解而非保证盈利|赞助可分担设施运营费，门票旅游产生收入，但收入仅可能抵消部分成本；总收入不能代替净利润检验。|赞助帮助支付成本→门票与旅游收入增加→抵消部分费用→仍需扣除全部相关成本→才可判断盈利
结尾：支持的具体门槛|有经济文化潜力不等于无条件应办赛；需预期收益能支持成本且风险被管理，才能保持支持立场。|经济文化收益→与成本比较→财务风险可管理→有条件支持办赛
''', '''
impose a heavy financial burden on|校|把负担落到承担者；impose a burden on + 人或机构，不用to。|Unexpected tuition increases can impose a heavy financial burden on low-income families.
transport infrastructure|校|交通基础设施；infrastructure不可数，build/improve + infrastructure。|Better transport infrastructure could connect rural workers with urban jobs.
grow in stature|熟|提高声望或地位；人或机构 + grow in stature，不等于规模增长。|A university may grow in stature when its research addresses important public needs.
financially viable|熟|财务上可行；become/be financially viable，收入与成本均需评估。|A free museum may remain financially viable if stable grants cover its operating costs.
gross revenue|熟|总收入而非净利润；generate/report gross revenue，利润需扣成本。|High gross revenue does not guarantee that an online retailer can cover delivery and storage costs.
''', '''
办赛财政负担的完整链条是什么？|中标后建设场馆交通配套，投入大量资源；若建造费用超过预算，主办方可能陷入债务。
“赛事展示并学习文化”的主语错在哪里？|赛事可以展示文化，学习文化的是参与者；要给第二动作补出participants。
赞助与门票收入为何不能直接证明办赛盈利？|它们是收入并可能抵消部分成本，净利润仍须扣除相关费用；gross revenue不等于net profit。
''', '换成城市建设新剧院：比较公共文化收益、收入和成本，写有条件支持。', 'A new theatre could attract visitors and provide space for local performances. It should proceed only where expected benefits justify construction and operating costs, since ticket revenue alone does not demonstrate a net profit.')

add(24, 'Sporting Success: Fitness and Mental Attitude', '双边讨论＋个人观点题', '体能与积极心态应结合；个人速度力量项目更侧重体能，策略团队项目也重心态协作。', '''
开头：两种成功基础|rest on与hinge on对应体能和心态，后文不是证明一项无用，而是比较在不同项目中的侧重点。|成功依赖体能的观点→成功更依赖心态的观点→按项目比较
主体一：体能优势的条件|速度力量可让运动员在个人项目中领先；假设其他技能相近时短跑者更强的例子，支持体能重要而非只由体能定胜负。|速度力量更优→相近技术条件下表现更好→个人项目可能占优→接力团队也可受益
主体二：积极心态与团队增益|身体更强的对手未必获胜，信念、主动性、坚持可让团队超越成员简单相加；心态只是与体能一起贡献，不保证独立决定结果。|对手身体条件强→团队信念与坚持→协作形成整体增益→可能战胜强手
观点结尾：按项目分配重点|速度力量项目可更侧重体能，策略协作项目需积极心态帮助个体突破并配合；结合两者才回应双方而不绝对化。|整合体能与心态→个人项目重速度力量→团队策略项目重配合→个人共同发挥推动团队
''', '''
have the edge over their competitors|熟|具有竞争优势；have the edge over + 对手，不等于保证获胜。|Applicants with practical experience may have the edge over their competitors.
hinges more on|熟|更依赖某基础；hinge on + N/V-ing，more需比较对象。|The success of online learning may hinge more on consistent feedback than on expensive software.
greater than the sum of its parts|熟|整体产生协作增益；be greater than the sum of its parts。|A research group can be greater than the sum of its parts when members share different skills.
overcome strong opponents|校|战胜强劲对手；overcome + N，勿用make sb over。|A small firm may overcome strong opponents by serving a neglected market.
push their limits|校|突破自身能力边界；push + 所有格 + limits，常用复数。|Challenging projects can encourage students to push their limits.
''', '''
短跑例子加“competitors are otherwise similarly skilled”有什么作用？|控制其他能力差异，具体说明速度与力量如何提供优势，不声称体能独自决定所有比赛。
团队心态段怎样避免把一场胜利归因于唯一因素？|用may与alongside physical strength，说明信念主动性坚持可共同贡献成功。
结尾怎样区分两类项目的重点？|速度力量为核心的个人项目更看重体能；策略与团队项目中，心态有助突破个人边界和配合。
''', '换成团队学习：区分个人基础知识与协作心态，并解释整体增益。', 'Strong subject knowledge gives each student a useful foundation. A team can nevertheless become greater than the sum of its parts when members share ideas and persist through difficult tasks.')

add(25, 'High Sports Salaries: Justified', '双边讨论＋个人观点题', '支持高薪合理版：公众自愿付费形成商业收入，运动员有理由分享贡献创造的收入。', '''
开头：共享题目，保留独立立场|双方比较体育高薪与重要职业报酬；此版后文支持高薪合理，与下一篇同题反对版分别学习。|体育薪资很高→有人视为合理→有人以其他职业贡献质疑→比较公平标准
主体一：社会贡献尺度下的反方|如果薪水按社会贡献和责任排序，外科医生、科研者和国家治理者有重大职责，体育报酬显得过高；先充分理解反方标准。|薪酬应反映社会贡献→其他职业责任重大→体育高薪比较下显得过高
主体二：才华、投入与职业压力|卓越人才稀少，持续竞争、短职业期和媒体压力提供支持理由；注意the number配small，媒体聚焦内才会隐私减少。|卓越运动员稀少→技能投入受持续考验→职业期较短→媒体压力与隐私损失→提供高薪理由
观点段：市场解释接上公平桥梁|受欢迎能解释高薪形成，还需观众自愿付费、运动员创造商业收入及合理分享这一桥接，才能讨论合理性。|公众支持与自愿付费→运动员创造商业收入→合理分享所创造收入→公平不只按社会责任比较
结尾：明确采用的标准|承认贡献责任值得考虑，但加入公众支持与收入创造；在此商业分配标准上支持高薪可充分合理。|贡献责任并非唯一标准→公众支持和收入也相关→在此基础上高薪可合理
''', '''
in proportion to|熟|按比例对应；be in proportion to + N，说明评价尺度。|Training budgets should be in proportion to employees' actual learning needs.
exceptional talent|校|卓越才能而非泛指真实才能；have/possess exceptional talent，talent不可数。|Scholarships can help students with exceptional talent continue their education.
in the spotlight|校|受到公众密切关注；be in the spotlight，区别out of。|A public official in the spotlight may face intense scrutiny over everyday decisions.
generate commercial revenue|校|产生商业收入；generate + revenue，不自动等于净利润。|Popular educational videos can generate commercial revenue for their creators.
a substantial share of it|校|分享前述收入的较大份额；receive a share of + N，it须清楚回指。|If a community business succeeds, local workers should receive a substantial share of its benefits.
''', '''
社会贡献标准为什么可能得出体育薪资过高？|医生科研者等承担重大社会责任，若按此比例分配薪酬，运动员报酬相对显得过高。
市场受欢迎为什么还不足以单独证明公平？|它只解释收入形成；需补观众自愿付费、运动员创造收入、因此合理分享收入的规范桥梁。
本版结论与反对版的关键差别是什么？|此版把公众支持和商业收入创造纳入公平标准，因此支持高薪在此基础上可合理。
''', '换成内容创作者收入：用自愿付费到合理分享收益的链条写两句，不只说受欢迎所以公平。', 'When viewers voluntarily subscribe to an educational channel, its creator helps generate commercial revenue. Receiving a substantial share of that income can be reasonable when the creator provides the work that attracts those subscriptions.')

add(26, 'High Sports Salaries: Excessive', '双边讨论＋个人观点题', '反对高薪合理版：按社会贡献比较，稀缺才能、投入与压力并非运动员独有，体育报酬过高。', '''
开头：同题另一独立答案|保留与合理版相同的双方介绍；学习时关注后续采用的社会贡献尺度，不把共享前三段误当重复贴错。|体育薪资很高→合理与不公平两方争论→本版按社会贡献判断
主体一：贡献与报酬比较|把运动员薪水与外科医生、科学家、治理者薪水作同类比较，社会责任标准下前者显得过高。|以社会贡献为薪酬标准→其他职业承担重大责任→比较相应薪水→体育报酬显得过高
主体二：公平呈现支持高薪理由|仍完整承认卓越人才稀少、投入、短职业期和媒体压力；反驳需要回应这些理由，而非删除正方。|人才稀少→技能奉献与持续竞争→短职业期及媒体压力→正方据此支持高薪
观点段：同一标准应适用他人|科学家也稀少且长期投入，农业研究提高产量可改善粮食供给；科研压力亦重大，所以这些特质不足单独证明运动员应获远高报酬。|科研者也有稀缺才能与长期投入→提高产量→改善粮食供给→承担重大压力责任→相同奖励原则应适用于其他职业
结尾：修正立场冲突|用excessive与社会贡献比较重申反对，删去原来误贴的fully justifiable；不是否认任何运动员收入都可支付。|贡献责任应作为标准→才能投入压力不足单独证明巨大差距→相对其他职业体育薪资过高
''', '''
when compared with|校|比较同类对象；A appears + 形容词 + when compared with B，被动省略逻辑主语清楚。|Online courses may appear inexpensive when compared with residential programmes.
few in number|校|数量稀少；复数人或物 + be few in number，区别the number is small。|Qualified interpreters may be few in number in remote hospitals.
make breakthroughs|校|取得突破；make breakthroughs in + 领域，不能只写breakthrough当动词。|Long-term investment can help engineers make breakthroughs in energy storage.
improving food security|校|说明粮食保障结果；improve + food security，也可分词补充前述行动结果。|Better rural roads could reduce delivery losses, improving food security in isolated communities.
on the basis of their social contribution|校|明确评价依据；on the basis of + N，不与市场形成机制混为一谈。|Community grants could be assessed on the basis of their social contribution.
''', '''
本版怎样回应才华、投入与压力支持高薪的理由？|说明科学家等也具备稀缺能力、长期奉献和重大压力，故这些条件不能单独证明体育的巨大薪资优势。
农业科学家的假设例子通过哪些步骤显示社会贡献？|开发高产水稻，提高粮食供给可靠性，改善粮食安全并帮助饥荒风险地区。
为什么结尾必须由fully justifiable改为excessive？|前文以社会贡献比较反对高薪，fully justifiable会直接支持相反立场；excessive才与本版论证一致。
''', '换成娱乐明星与护理人员的薪资：公平解释明星收入形成，再用社会贡献标准提出评价。', 'Popular entertainers may generate substantial revenue through voluntary ticket sales. However, when pay is assessed on the basis of social contribution, the much lower rewards received by essential care workers deserve scrutiny.')

def plain(s):
    return s.replace('**', '')

assert len(records) == 26
for r in records:
    assert len(r['paragraphNotes']) == len(r['essayParagraphs']), (r['code'], 'paragraph notes')
    assert 5 <= len(r['collocations']) <= 8
    assert 3 <= len(r['questions']) <= 5 and len(r['answers']) == len(r['questions'])
    text = '\n\n'.join(map(plain, r['essayParagraphs']))
    for c in r['collocations']:
        assert c['phrase'].casefold() in text.casefold(), (r['code'], 'phrase missing', c['phrase'])
    for c in r['corrections']:
        assert 0 <= c['paragraphIndex'] < len(r['essayParagraphs'])
        # One source quotation deliberately omits the sentence-leading "Some".
        revised = plain(c['revised'])
        p = plain(r['essayParagraphs'][c['paragraphIndex']])
        assert revised.casefold() in p.casefold(), (r['code'], 'correction anchor missing', revised, p)
    # Round trip into source retains all Markdown emphasis and punctuation.
    assert '\n\n'.join(r['essayParagraphs']) in SOURCE
    assert all(2 <= len(n['chain']) <= 5 for n in r['paragraphNotes'])

destination = ROOT / 'data/nine.json'
destination.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'records':len(records), 'paragraphs':sum(len(r['essayParagraphs']) for r in records), 'corrections':sum(len(r['corrections']) for r in records), 'collocations':sum(len(r['collocations']) for r in records), 'recallPrompts':sum(len(r['questions']) for r in records), 'output':str(destination)}, ensure_ascii=False))
