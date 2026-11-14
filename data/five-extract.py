"""Extract exact source paragraphs; enrich with original Chinese teaching and transfer exercises."""
import json, re
from pathlib import Path
ROOT=Path('/Users/andy.lu/🟢learn-something/learn-ielts-essay')
text=(ROOT/'materials/five-topics.md').read_text()
pattern=re.compile(r'^\*\*((?:A|B|T|C|R)\d+)．(.*?)｜(\d+)词\*\*$',re.M)
heads=list(pattern.finditer(text))
records=[]
for i,h in enumerate(heads):
    section=text[h.end():heads[i+1].start() if i+1<len(heads) else text.index('**这批文章最值得继续沿用的写法**')]
    q,body=section.split('**小修版**',1)
    question='\n'.join(re.sub(r'^> ?', '',line) for line in q.splitlines() if line.startswith('>')).strip()
    essay,corr=body.split('**最值得理解的三处调整**',1)
    paragraphs=[p.strip() for p in essay.strip().split('\n\n') if p.strip()]
    explanations=re.findall(r'^([123])．(.*?)(?=\n\n|\Z)',corr,re.M|re.S)
    assert len(explanations)==3,(h[1],explanations)
    records.append(dict(id='five-'+h[1].lower(),code=h[1],title=h[2],sourceGroup='five',sourceHeading=h[0],declaredWords=int(h[3]),question=question,essayParagraphs=paragraphs,corrections=[dict(title='',original='',revised='',explanation=v.strip(),paragraphIndex=0) for n,v in explanations]))

def note(role,explanation,chain):
    return dict(role=role,explanation=explanation,chain=chain.split('→'))
# Each note describes this paragraph's actual content, rather than a generic outline.
DETAILS={
'A1':('Who Can Create Art?','双边讨论与个人观点','人人能以艺术表达自己；广受认可的作品通常需要更成熟的技艺。',[
('开头｜拆开两个评价标准','开头先承认艺术的重要性，再把争论拆成参与创作与获得广泛认可两个层面。自己的答案直接出现，后文可以分别解释两个标准。','艺术重要→谁能创作有分歧→人人可表达→名作通常需技艺'),
('主体一｜低门槛支持普遍参与','从艺术是表达个人经验的渠道出发，以纸笔绘画说明工具要求低。例子证明人们有机会创作，而不是证明每个人都能成为大师。','独特想法与经验→借艺术媒介表达→纸笔门槛低→人人可以参与'),
('主体二｜认可标准支持专业能力','另一方把艺术理解为高质量作品，判断依据包括技术与洞察社会现象的能力。usually和generally保留例外，避免把非专业者排除在外。','重视作品质量→技巧或社会洞察→技艺更加成熟→作品较易获得认可'),
('个人判断｜用定义化解表面冲突','末段区分艺术本身的表达功能与社会通常讨论的艺术价值、商业价值。训练可以解释名作常出自专业人士，但不能证明别人没有创作资格。','艺术作为表达→人人能够创作→社会认可另有标准→训练帮助获得认可')],
[('低门槛为何支持人人创作，却不能证明人人能创作名作？','纸笔降低参与成本；广泛认可还受技术与作品洞察力影响。'),('末段为何用explain而非justify？','专业训练能解释名作较常出自专业人士，不能证明只有他们才有资格创作。'),('本文立场的两个层次分别是什么？','自我表达的艺术人人可做；广受认可的作品通常需要更成熟的技能。')],
'迁移到公民科学：用两三句区分人人可以参与收集数据与人人能独立完成可靠科研；给出质量标准。','Anyone can contribute to citizen science by recording local wildlife. However, producing reliable scientific findings generally requires careful methods and relevant expertise. A low barrier to participation does not remove the need for quality control.'),
'A2':('What Art Reveals About Life','直接问答：艺术的独特作用','艺术传达内在情感、共同文化经验与审美价值，补充科学解释。',[
('开头｜直接回答艺术告诉我们什么','科学的重要性无需否认；论点是单靠科学解释未必能充分传达人类经验和审美价值。cannot fully capture限定不足的程度，避免制造绝对对立。','科学技术受重视→艺术仍受重视→传达人类经验与审美→补充科学解释'),
('主体一｜从创作者走到受众理解','个人用艺术表达喜悦、失落等感受，受众由此理解内在体验；社会层面，作品呈现共享价值和历史变化。这里真正回答的是观者知道了什么。','表达思想感受→他人理解内在经验→作品反映共享价值→理解时代与价值变化'),
('主体二｜功能之外的审美意义','手机既需要运行系统，也依赖工业设计。例子把技术能做什么与人为何觉得美分开，说明实用功能不能单独决定意义与吸引力。','科学解释功能→功能不等于美与意义→手机也依赖工业设计→艺术显示日常审美追求'),
('结尾｜汇总互补关系','结尾重提个人感受、文化经验、审美三项答案。科学解释世界的运作，艺术进一步传达生活在其中的感受，保持开头的互补立场。','个人感受→共享文化→审美价值→补充科学知识')],
[('自我表达之后需要补哪一步才能回答题目？','作品让别人理解喜悦、失落等经历从内部感受起来是什么样。'),('手机例子怎样说明艺术的价值？','技术提供功能，工业设计体现视觉美感；功能本身不能决定人觉得什么美或有意义。'),('为何结尾用complement而不是取代科学？','本文承认科学的解释作用，艺术补充它未充分传达的主观与文化经验。')],
'迁移到历史学习：用两三句解释历史小说如何补充年代表，保留两者的作用边界。','A timeline explains when historical events occurred, while a novel can convey what uncertainty or loss might have felt like to ordinary people. These personal perspectives complement factual knowledge, although fictional scenes should not be treated as historical evidence.'),
'A3':('Arts Funding and Public Services','同意与不同意','先满足紧迫公共服务需求，但反对撤销艺术经费；按基本需求与文化收益平衡预算。',[
('开头｜支持基本服务但反对撤资','开头同时确定预算优先次序与反对的政策力度。承认基本服务必须满足，并不接受把艺术经费全部抽走。','预算分配争议→基本服务需满足→艺术仍有投资理由→反对撤销经费'),
('主体一｜说明服务改善的紧迫性','无障碍设施损坏使残障者出行困难；投入可减少障碍、提升独立生活能力。比较对象是追加艺术支出与紧迫服务需求，不是不同群体有没有文化需求。','设施损坏或失修→残障者出行受阻→改善无障碍设施→独立生活与便利出行'),
('主体二｜保留艺术的个人和文化收益','艺术课程让人表达和放松，博物馆等作品帮助人们理解历史价值变化。这两类收益解释保留预算的理由，并不否定前段服务的紧迫性。','艺术参与→表达情绪与维持心理福祉→欣赏作品→理解历史与共享文化'),
('主体三｜有条件地比较边际收益','只有基本服务需求已经满足，继续增支的额外收益才可能变小。少量艺术资金转出可能只略改善服务，却损失宝贵参与机会，因此要比较增量收益。','基本服务已满足→追加服务收益可能递减→转走少量艺术款改善有限→保留文化参与机会'),
('结尾｜回到预算分配标准','重申紧急服务优先与艺术投资合理两条判断，用明确标准平衡基本需求和文化机会。结尾没有假定现行预算已经最优。','满足紧迫服务→承认文化及个人收益→采用清晰标准→平衡预算')],
[('本文反对的是支持公共服务，还是撤掉艺术经费？','反对撤掉艺术经费，同时支持先满足基本公共服务。'),('收益递减论证必须补什么前提？','基本公共服务需求已得到满足，才讨论追加投入的较小收益。'),('无障碍设施例子比较的是什么？','改善服务的紧迫性与追加艺术支出，而非残障者是否能欣赏艺术。')],
'迁移到学校预算：承认基础课堂设施优先，再用条件句解释为何仍应保留课外活动经费。','Essential classroom repairs should take priority when safety is at risk. Once these needs have been met, further spending on decoration may bring smaller benefits than retaining a modest budget for extracurricular activities. Allocation should reflect both basic needs and opportunities for participation.'),
'B1':('Heritage Preservation or Roads?','同意与不同意','满足交通需求同时保留老建筑保护经费，兼顾交通与文化经济价值。',[
('开头｜明确预算取舍','道路建设的需求得到承认，但不足以否定修复保护老建筑的政策。两个支出项目必须按理由比较，不能因一项有益便取消另一项。','公共预算有限→道路需求存在→老建筑仍有保护理由→不能全转道路'),
('主体一｜道路改善如何惠及通勤者','拥堵损害身心体验；修立交、移除瓶颈可能减少被堵时间。might使效果与设施实际作用相匹配，并未许诺修路必然消除拥堵。','高峰拥堵→通勤压力与耗时→立交和瓶颈改善→通勤体验可能提升'),
('主体二｜文化载体与旅游经济','老建筑保留文化的实体证据，帮助后代理解身份；修复后的建筑还可能吸引游客。假设保留古寺的例子具体呈现文化资源如何转化为经济吸引力。','保留实体文化证据→延续文化认同→修复古建筑吸引游客→产生旅游经济价值'),
('主体三｜道路较完善时的追加收益','这段只在道路已经较发达的情况下讨论收益递减。继续转入保护款可能改善有限，而少量保护投资仍可保留文化价值。','道路已较完善→每单位追加收益可能减少→转移保护款改善有限→保留经费维护文化价值'),
('结尾｜给出双重标准','道路需求应得到满足，老建筑的文化及经济重要性也支持继续出资。严格标准要兼顾两者，而非简单维护既有分配。','交通需求→遗产文化与经济收益→维持保护资金→按标准平衡两项需求')],
[('古寺例子是现实证据还是假设？','是假设城市保留古寺来吸引游客，没有把未经核实的具体城市案例当事实。'),('道路收益递减需要什么条件？','道路基础设施已较完善，才可能出现追加投资改善有限。'),('老建筑的两类价值如何展开？','实体遗产保存文化认同；历史特色吸引游客并带来经济活动。')],
'迁移到图书馆与网络建设：用有条件的边际收益比较说明为何不应把图书馆经费全部投入宽带。','Where broadband coverage is already extensive, additional investment may bring only limited improvements. Retaining a modest library budget can still preserve access to quiet study space and personal assistance. Both forms of infrastructure should be assessed against local needs.'),
'B2':('More Parks in Every Town?','同意与不同意','缺少设施的地区可增建，但所有城镇一律多建未必财政可行，也未必解决时间障碍。',[
('开头｜把可行性与效果分开','运动不足引出增建公园的提议。作者分别检验是否有钱长期实施，以及是否真能让人运动，两项标准不能互相替代。','运动不足→提议所有地方增建→检验财政可行性→检验健康效果'),
('主体一｜承认空间不足时的收益','久坐与工作压力减少日常运动，缺场地进一步恶化问题。增加公园能提供散步和慢跑的场所，所以在设施不足地区有针对性。','久坐与压力→运动减少→空间不足加重限制→新增场地提供运动机会'),
('主体二｜建造之外还有持续成本','地方预算同时面对医疗、交通、养老金等需求。欠富裕地区不仅要支付建设费，还要持续维护和清洁，增建可能挤占其他领域。','多领域争夺预算→增支空间有限→建设加持续维护→可能削减其他服务'),
('主体三｜时间障碍不能靠扩地解决','场地不足和工作学习负担可以同时限制运动。若人没有时间，增加公园也未必改变行为；因此需要意识教育与日程内的运动时间。','工作学习负担重→缺少运动时间→新公园可能闲置→提高意识并安排运动时间'),
('结尾｜按实际障碍选择措施','公共健康值得重视，但所有地方增建既可能昂贵，又可能错过主要障碍。结尾要求意识和运动机会配合设施，保留条件判断。','公共健康需关注→一律增建可能难负担→时间障碍仍在→意识与机会共同改善')],
[('financially viable与effective分别检查什么？','前者检查能否负担并持续实施；后者检查能否真正改善运动与健康。'),('公园的持续成本有哪些，影响什么？','维护与垃圾管理等成本会继续占用预算，可能挤压其他公共服务。'),('针对工作学习挤占运动时间，应补什么措施？','在工作学习日程中安排运动时间，并提高经常运动的意识。')],
'迁移到数字图书馆：说明新增资源不能自动解决学生缺少阅读时间的问题，并给针对性措施。','A digital library can make books easier to obtain, but access alone may have limited effects when students lack time to read. Schools could protect a short reading period each day. This would address a different barrier from the availability of books.'),
'B3':('Housing, Parks and Commuting','双边讨论与个人观点；比较最佳方案','不认为以公寓取代绿地是最佳方案；针对拥堵与职住距离采取措施并保留绿地。',[
('开头｜回应最佳而非仅有效','承认住房可能缓解通勤，但作者反对它是最佳，因为它忽略其他主要成因并牺牲绿地。后文需要比较替代措施能解决什么。','通勤耗时→以公寓替代绿地→其他成因未解决→不认定为最佳'),
('主体一｜住房缩短通勤的条件','预算有限的职工住在外围导致路程长。新增中心公寓只有同时可负担且靠近工作地点，才可能让这群人搬近并省下时间。','预算有限住外围→通勤距离长→新增住房可负担且近工作→节省通勤与增加休息'),
('主体二｜承认距离并补入拥堵','这一段不否认距离重要，而是指出慢速交通也会耗时。只建住宅可能留下拥堵问题，因此效果有局限。','距离影响耗时→慢速交通也影响耗时→早出门仍可能堵车→住房单项措施有限'),
('方案比较｜针对原因并避免绿地损失','改善瓶颈服务道路通勤者；企业迁址只有更接近员工住处才缩短距离。适宜土地与较低租金使迁址可能可行，绿地的运动休闲价值则得以保留。','改善交通流与适当迁址→减少拥堵或职住距离→考虑租金与可用土地→保留休闲运动绿地'),
('结尾｜按条件选择替代措施','用其他通勤成因和绿地价值再次回答best。考虑道路改善及适当企业迁址，既针对问题也减少替代公园的损失。','其他成因仍存在→绿地有价值→考虑交通与迁址→减通勤且保绿地')],
[('中心新增住宅要满足哪两个条件才帮助目标通勤者？','他们负担得起，且住宅靠近他们的工作地点。'),('指出拥堵存在能否证明距离无关？','不能；距离有作用，但住房方案忽略拥堵等其他重要成因。'),('企业搬到郊区何时才缩短通勤？','搬迁使企业更接近员工居住地，且选址具备适合土地等条件。')],
'迁移到教育：讨论延长上课时间是否最佳，给出另一原因与更针对性的替代措施。','Longer lessons may provide more practice, but they are not necessarily the best way to improve learning. When students misunderstand basic concepts, additional repetition may have limited effects. Targeted feedback can address those gaps without sacrificing all their free time.'),
'B4':('Parks or Shopping Centres?','同意与不同意','公园和商场都有作用，应依据新城需求规划，不预设公园设施数量必须更多。',[
('开头｜价值不直接决定数量优先','公园重要是双方可以接受的起点，作者反对从重要性直接推出它们应比商场优先且更多。论证聚焦具体比较要求。','公园体育设施重要→提出数量优先→重要性不足以证明优先→继续比较商场作用'),
('主体一｜降低门槛并形成社区联系','低成本设施使付不起健身会员的人也有运动机会；公园聚会又让居民交流。分别说明身体活动和心理归属两条收益。','低成本设施可达可用→居民更易运动→公园促进交流→健康与社区归属'),
('主体二｜商场也承担多种需求','商场可同时购物、社交、娱乐、运动，集中采购省时且停车便利。室内空间遮蔽天气，使其成为另一类休闲选择，而非只有消费功能。','商场多功能→购物社交休闲集中→节省时间与便利停车→室内遮蔽天气'),
('结尾｜以需求代替固定比较','把公园优势与商场作用同时纳入规划，按新城具体需要决定建设。没有把题目夸大为强制配额，只拒绝预设数量关系。','公园有健康收益→商场满足多种需求→调查新城需要→按需求决定数量')],
[('公园重要为什么不能直接推出必须比商场更多？','商场同样满足购物与休闲等需求，数量应根据具体地方需求比较。'),('低成本为何是体育设施段的关键条件？','它解释负担不起健身会员的居民为什么也能实际使用设施。'),('商场对天气的优势该怎样限定？','室内区域能提供遮蔽，不表示完全不受任何极端天气影响。')],
'迁移到学校课程：用两三句解释体育和艺术都重要，但课时比例应依据学生需要决定。','Sports can improve physical fitness, while arts classes provide opportunities for self-expression. These benefits do not establish a fixed ratio between the two. Schools should allocate lesson time in accordance with students’ needs and the opportunities already available to them.'),
'T1':('Television at Home and School','同意与不同意；分场景评价','合适内容有教育价值；学校不应挤占教师教学，家庭可在内容和时长指导下观看。',[
('开头｜家庭与学校分开判断','电视教育价值引出定期观看建议，作者把学校挤占教学与家庭受监督观看分开。counterproductive带有反效果，必须与替代教师授课的条件连用。','电视有教育价值→提议定期观看→学校或挤占教学→家庭可受指导观看'),
('主体一｜内容选择决定学习机会','纪录片帮助理解生态和环境，儿童节目提供日常表达。增加观看只是在适合内容已选好的前提下增加学习机会，不能直接推出学习成效必然更好。','选合适纪录片与儿童节目→视觉对话吸引注意→了解世界并学表达→学习机会可能增加'),
('主体二｜碎片观看与系统教学对比','看到授粉现象会感到惊奇，但教师能按顺序解释概念及原因。学校时间若被观看替代，就可能损失系统知识和互动讨论。','节目呈现授粉现象→学生惊奇但理解未必系统→教师分步解释概念→避免屏幕挤占教学'),
('主体三｜家庭观看的风险与配套','无人监督容易让娱乐占用过多时间，持续屏幕还可能挤掉户外活动。家长限定内容时长、安排休息，让教育与娱乐取得平衡。','缺少监督→过多娱乐屏幕→眼疲劳与户外时间减少→家长指导及限时休息'),
('结尾｜重申使用条件','定期看电视的教育意义不能成为替代教师授课的理由；家庭观看仍可允许，条件是父母帮助控制内容和程度。','认可电视教育→学校避免替代教学→家庭保留观看→父母帮助适度使用')],
[('授粉例子要证明什么区别？','节目展示现象，教师能逐步解释授粉的概念和必要性，实现系统学习。'),('什么条件下学校观看可能counterproductive？','它挤占或替代教师主导的教学，而非所有课堂视频都一定有害。'),('家庭观看需要哪三类安排？','选择合适内容、限制时长、定期屏幕休息并保留户外活动。')],
'迁移到课堂AI：先认可其资源优势，再限定不能取代教师系统指导，写两三句。','AI tools can give students quick access to examples, provided that the material is accurate. However, replacing teacher-led instruction with unguided use may leave gaps in understanding. Teachers should connect selected outputs to clear learning objectives and check how students interpret them.'),
'T2':('Watching Programmes Alone','利弊权衡','保持其他共同活动时，独看带来的选择自由和便利可以超过减少共同观影的损失。',[
('开头｜给权衡判断加条件','独看可能带来情感隔离，但保留其他社交活动时可总体积极。条件提前出现，为后文如何弥补交流损失做准备。','独自观看增加→可能情感孤立→保留其他社交活动→便利自由总体可更大'),
('主体一｜具体决策展示自主收益','悬疑片与爱情片的偏好冲突会让其中一人妥协；独看可自主暂停、换节目、重看与切换设备，不必协商。便利通过一组具体行为落地。','多人偏好不同→一方可能妥协→独看自主控制节目与节奏→减少协商并尊重偏好'),
('主体二｜替代渠道缓解交流损失','共同观影中的讨论和玩笑有助关系，独看减少这个渠道。但真正重要的是互动，若人们继续共餐、散步、购物，社交需要仍可满足。','独看减少共看片段交流→关系维系机会变少→保留共餐散步等活动→其他互动补足需要'),
('结尾｜依据可替代程度权衡','不否认独看期间交流较少，而是依据日常互动能补充这个缺点来判断。保留其他共同活动的条件使便利与灵活性可超过损失。','承认独看交流少→日常共同活动补足→社交需要可满足→便利与灵活性可胜出')],
[('独看自由具体体现在哪些操作？','自主选片、暂停、切换节目、重看及换设备，不必和别人协商。'),('缺点可缓解依赖什么条件？','观众继续保持共餐、散步、购物等其他共同活动和互动。'),('本文按什么依据比较利弊？','共同观影损失的互动渠道可以被其他活动替代，同时保留独看便利。')],
'迁移到远程办公：比较自主安排与同事联系减少，用具体配套措施限定你的利弊判断。','Remote work gives employees greater control over their schedules, but it can reduce informal contact with colleagues. This drawback may be mitigated by regular team discussions and occasional shared activities. Where such interaction is maintained, flexibility can outweigh the loss of daily office contact.'),
'T3':('Children and Television','双边讨论与个人观点','合适节目可帮助语言与知识学习；适度观看和成人引导可以控制风险。',[
('开头｜双方极端观点与作者条件','一方认为电视全面有害，另一方重视知识获取。作者认可双方值得考虑，但答案落在适度与指导，不照搬任何绝对判断。','全面有害观点→知识收益观点→双方均有可讨论理由→作者主张适度及成人指导'),
('主体一｜条件化说明身体与行为风险','长时间不休息可能眼疲劳并挤掉户外活动；部分儿童难辨虚构现实，可能模仿暴力。may、some避免把潜在机制写成普遍确定事实。','长时观看缺休息→眼疲劳与户外时间减少→虚实辨别困难→部分儿童可能模仿暴力'),
('主体二｜视听材料如何帮助学习','模仿角色语言可辅助语言学习，分步骤儿童节目帮助理解世界。英语动画只是语言学习的一部分，教师精选片段仍需要教学整合。','角色语言吸引模仿→辅助语言学习→分步视听呈现→精选片段支持知识教学'),
('个人判断｜把风险连接到具体干预','问题主要落在持续无休息的方式；限制电视并增加户外活动回应身体风险。成人讨论年龄适合节目中的暴力，帮助区分虚构及理解后果，同时避开明显不适内容。','识别过度观看方式→限时休息与户外活动→讨论虚实和行为后果→避开不适内容降低风险'),
('结尾｜把收益与风险放入同一条件框架','适合的节目可支持语言与知识，不受限制的观看才扩大风险。父母和教师帮助儿童正确使用，比放任不限时不限内容更符合前文。','合适节目带来学习→无限观看放大问题→父母教师引导→适度获取收益')],
[('为什么不能把电视本身等同于身体伤害？','风险与长时间观看、缺少休息及替代户外活动等使用条件有关。'),('动画为何不能单独保证双语能力？','它只是语言学习的一部分，可提供模仿机会，仍需其他学习与指导。'),('行为风险段的具体干预有哪些？','讨论年龄适合节目中的暴力，区分虚构现实，理解行为后果，并避开明显不适内容。')],
'迁移到电子游戏：把使用方式与媒介本身分开，写出两个具体干预来保留收益。','Games can provide opportunities for problem-solving, while prolonged play may displace exercise or sleep. Parents could agree on time limits and discuss age-appropriate content with children. These measures target risky patterns of use while preserving some benefits of the medium.'),
'C1':('Executive Pay and Contribution','同意与不同意','责任规模和个人贡献可以支持高管高薪，但约定工资不等于低贡献时的巨额奖金。',[
('开头｜高薪合理性的限制条件','作者承认薪酬应与表现贡献相称，并主张责任与贡献可支持更高高管报酬。立场是有条件的支持，不替所有现存差距辩护。','高管角色受重视→薪差引争议→薪酬须匹配贡献→责任规模可支持高薪'),
('主体一｜公平反对意见','反方质疑的是报酬超过表现应得的程度，尤其企业业绩差却获得大奖励。performance-based给出评价原则，而非断言所有高管薪水都过高。','薪酬看贡献责任→部分高管奖励过度→业绩差仍获大奖励→绩效原则受到质疑'),
('主体二｜评价管理贡献的范围','普通员工往往按个人工作评价，领导者决策却影响全团队。成功重组公司是一个假设例子，说明高薪可承认管理者改善整体生产力的贡献。','个人岗位贡献→管理影响全队→决策改善整体生产力→贡献规模可支持高薪'),
('主体三｜合同工资与绩效奖金分开','公司失败可能有管理者无法控制的原因，人才也不保证成功。已经履职的约定工资应支付，但不能据此证明贡献不足时巨额绩效奖金合理。','外部因素影响失败→优秀人才也不保证成功→工作应获约定工资→低贡献不支持巨额奖金'),
('结尾｜回到责任与自身贡献','结尾用责任规模补充个人贡献标准；企业成败不单独决定薪水合理性，必须看高管本人的作用与职责。','考虑个人贡献→考虑责任规模→不能只按公司成败→有条件认可高薪')],
[('普通员工与管理者贡献的评价范围有何区别？','前者多看个人工作，后者还要看其决策改善整个团队表现的作用。'),('失败企业高管享有约定薪水是否证明巨额奖金合理？','不能；合同工资是工作报酬，绩效奖金仍需贡献与表现依据。'),('假设重组例子实际证明什么？','高管若改善全公司生产力，其贡献范围可支持比个人岗位更高的报酬。')],
'迁移到科研团队：区分普通成员贡献与项目负责人的协调责任，同时限制绩效奖励判断。','A project leader may coordinate resources that affect the performance of an entire research team. This wider responsibility can justify higher compensation when it reflects a real contribution. However, an agreed salary does not automatically justify a large bonus for an unsuccessful project.'),
'C2':('A Four-Week Leave Entitlement','同意与不同意','支持至少四周年假以兼顾持续恢复和日常休息，配合提前排班与代班。',[
('开头｜把休假视为效率措施','年假看似中断流程，但作者将其视为支持工作效率的安排。开头锁定四周这个具体时长，后文须说明为何不只是少量假期。','提升工作表现目标→至少四周年假提议→承认流程干扰→视为效率安排'),
('主体一｜过劳如何损害持续表现','长时间工作缺乏恢复引发压力、情绪和士气问题；工作相关疾病可能导致离职。适当休假通过恢复状态支持持续表现。','工作过久缺休息→压力情绪士气受损→疾病与可能离职→充足年假支持持续表现'),
('主体二｜为四周提供安排层面的理由','五天假常被零散用掉，难有持续恢复；四周可安排两周连续恢复及两周全年短休。这是合理的最低安排论证，不是科学证明精确天数。','五天零散使用→持续休息不足→两周长休加两周短休→兼顾恢复与全年动力'),
('反驳段｜用组织安排解决实施障碍','难代班的职责可能让流程受阻，管理者需提前协商时间、错峰休假并训练同事覆盖关键职责。四周权利不意味着所有假一次休完。','职责难被替代→工作流程受扰→提前协商错峰与交叉培训→提升休假方案可行性'),
('结尾｜把条件写进支持立场','短期效率干扰得到承认，持续与定期恢复支持四周作为合理底线。人员和时间安排妥当是该制度帮助表现的条件。','短期可能受扰→持续恢复及常规休息→合理最低年假→妥善安排支持表现')],
[('为什么不能从休假有益直接推出至少四周？','还需说明时长安排：两周连续恢复，另两周供全年短休。'),('四周年假是否要求一次全部休完？','不要求；错峰与分段休假可与提前代班共同维持流程。'),('怎样回应不可替代岗位造成的干扰？','提前协商休假日期，安排代班，并交叉培训同事覆盖关键任务。')],
'迁移到学校休息安排：解释连续恢复与短休的不同作用，并补排课条件。','A longer school break can provide sustained recovery, while shorter breaks throughout the term help prevent exhaustion. Combining the two may support learning more effectively than isolated days off alone. Schools would still need to plan the timetable carefully to protect essential teaching time.'),
'C3':('Business and Social Responsibility','同意与不同意','企业应在盈利之外减少伤害并承担社会责任，这也可支持长期成功与信任。',[
('开头｜盈利并非唯一考虑','企业对经济发展的贡献得到承认，但核心盈利目标不能成为只顾利润的理由。作者直接支持同时承担社会责任。','企业推动经济→核心目标盈利→不应只顾利润→还需承担社会责任'),
('主体一｜社会依赖与具体行动相连','盈利依赖服务客户及稳定繁荣的社会，所以责任既对社会有益也帮助企业长久成功。安全食品、假设捐助、可持续采购与安全公平劳动展示实际路径。','盈利依赖客户和社会→支持社会亦利长期经营→安全食品及公益采购劳动行动→责任有理由也有实施手段'),
('反方与回应｜自愿慈善和避免损害不同','企业不捐款未必可责，但污染把成本转给他人应承担责任。重视责任的员工与消费者还可推动改变并支持企业成功。','慈善可有自主选择→环境损害强加成本→应承担避免伤害责任→员工消费者选择鼓励责任经营'),
('结尾｜双向支持需写出机制','企业通过减少损害、支持社会赢得形象和信任；社会繁荣又支持经营成功。两个方向分别解释，避免仅用vice versa暗示因果。','责任经营减少损害→赢得客户信任→支持社会繁荣→社会繁荣支持企业成功')],
[('盈利依赖社会这一步怎样支持企业责任？','客户需求与社会稳定繁荣支持长期盈利，企业维护社会也在维护自身经营基础。'),('为何不能对不捐款与污染一律回答不应责怪？','捐款可属自愿选择，污染则给他人施加成本，责任性质不同。'),('餐馆例子怎样直接体现社会责任？','提供满足顾客需要的安全食品，将基本经营与避免对消费者伤害相连。')],
'迁移到大学：区分自愿捐助与减少运营伤害，并说明长期声誉收益。','Universities may choose whether to fund particular charities, but they should take responsibility for waste produced by their own operations. Reducing this harm benefits the surrounding community and can build public trust. A supportive local community may in turn help a university succeed.'),
'R1':('Mandatory Community Service','弊是否大于利：权衡','全面强制的弊大于利；鼓励自愿参与并提供适当培训能保留许多收益。',[
('开头｜评价强制要求而非志愿活动','志愿工作受赞扬引出要求所有青年参加的政策。作者直接回答全面强制弊大于利，后文不能只争论活动本身有没有好处。','志愿服务受赞扬→提出全民青年强制→承认活动收益→强制要求弊更大'),
('主体一｜青年与社区两类收益','青年帮助别人获得满足并练习人际技能，社区在适当监督下获得服务支持。监督条件避免暗示未经训练者能直接承担专业保护工作。','帮助别人→青年满足与人际成长→适当监督下提供服务支持→个人社区双赢'),
('反驳段｜额外强制带来的反效果','道德义务变成强制可能引发抵触，导致完成后更不愿志愿服务；部分工作需要资质，人数增加不保证服务质量。自愿与培训更贴合目标。','全面强制→抵触及未来不再志愿→增员也未必有专业能力→鼓励自愿并适当培训'),
('结尾｜用自愿替代比较额外得失','自愿参与可以保留不少技能和社区收益，且不对不愿参加者施加同样义务。这个比较具体解释强制新增的代价为何更难合理化。','自愿仍保留收益→强制额外施加义务→可能抵触且实施困难→弊大于利并保留自愿选择')],
[('本文比较对象是志愿活动好坏，还是强制要求的额外得失？','是强制要求相对自愿参与的额外得失。'),('强制为何可能counterproductive？','引发青年抵触，完成要求后更不愿未来参加志愿服务，损害长期参与目标。'),('为什么社区工作人员变多不一定更好？','一些服务依赖经验、资质及适当监督，人数不能直接替代这些条件。')],
'迁移到员工培训：承认培训收益，说明统一强制可能带来的额外成本，并提出定向替代。','Training can improve employees’ skills, but requiring everyone to attend the same course may waste time for experienced staff. A better option would be to assess individual needs and offer suitable modules. This can retain many of the gains without imposing an unnecessary obligation on every employee.'),
'R2':('Where Should Professionals Work?','双边讨论与个人观点','尊重专业人士职业选择自由；通过更好条件吸引留任或回流而非全面法律强制。',[
('开头｜训练国与选择自由','全球流动引出个人职业发展与培训国贡献的争议。培训地点是讨论对象，不等于个人国籍；作者明确倾向选择自由。','职业机会推动流动→海外发展选择→培训国希望留才→支持选择自由'),
('主体一｜解释留任要求的合理担忧','尤其公共资助培训使国家投入资源，当地服务带来更直接回报。人才离开可能减少技能和发展机会，这支持担忧却未独立证明强制合理。','公共教育培训投资→培养稀缺专业人才→当地服务直接回报→外流可能损失技能和机会'),
('主体二｜流动由个人处境推动','自由追求成功包括个人和职业领域。前景暗淡、生活质量差及机会有限会推动人才寻找更好的工作与生活，避免把外流简单归为不负责。','职业前景与生活条件差→个人发展受限→寻找更好机会与生活→形成专业人才外流'),
('个人判断｜道德责任不足以推出法律强制','培训国投资损失确实值得关注，但帮助它发展是道德责任，不能单凭此要求法律禁止离开。改善工作条件与经济保障可直接回应人才离开的原因。','承认投资损失→保留道德责任→道德责任不足以强制→改善条件吸引留任回流'),
('结尾｜尊重选择并鼓励贡献','承认外流对培训国的潜在损害，但保留个人自由。政策应让人才愿意留下或回来，把政府行动与前文原因连接。','潜在发展损失→仍尊重职业选择→政府改善吸引力→鼓励留下或回流')],
[('为什么培训国不能自动等同国籍国？','题目根据在哪里接受培训来讨论责任，并未限定专业人士的国籍。'),('公共投入为何只说更直接回报而非唯一回报？','本地工作直接服务社区，但海外工作也可能以其他方式产生回报，不能排除。'),('非强制留才政策怎样回应外流原因？','改善工作条件和经济保障，回应职业前景及生活机会不足。')],
'迁移到奖学金毕业生：承认公共投资的回报期待，再提出尊重选择的留任激励。','Public scholarships create a reasonable expectation that graduates will contribute to society. However, this moral obligation alone does not justify a blanket restriction on their career choices. Offering meaningful research opportunities may encourage them to stay or return voluntarily.'),
'R3':('Dangerous Sports and Regulation','双边讨论与个人观点','反对全面禁令；知情成年人自由有边界，以培训、标准及必要限额控制风险。',[
('开头｜给出监管胜过全面禁止的立场','安全与自由两种观点都被引出。作者支持合理监管，后文需要解释何种风险可以管理，以及自由适用于哪些参与者。','危险运动受欢迎→安全支持禁令→自由支持选择→作者支持合理监管'),
('主体一｜公平解释禁止一方','极限运动暴露参与者于严重伤害风险，追求刺激的青年可能忽视危险。禁令只有被有效执行才可能减少伤害，而非宣称必然消除事故。','高风险活动→可能忽视危险→严重或长期伤害→有效执行禁令可能减少伤害'),
('主体二｜类比提炼有条件的自由','篮球和滑雪也有受伤风险，说明有风险本身不够支持全面禁止。类比并未把风险大小等同；自由限定于理解风险的成年人且不危及他人。','普通运动也有风险→风险存在不足以全面禁止→成人理解风险→不让他人承受不合理危险'),
('个人判断与方案｜把公共风险落实为监管','安全标准降低参与风险，救援人员与公共资源也需要保护。高难路线培训要求对应能力不足，拥挤或救援承压时限额对应容量风险。','保留成年人选择→安全标准减少风险→救援风险及资源压力→按培训与容量实施合理监管')],
[('普通运动的类比能证明危险运动风险相同吗？','不能；它只说明存在风险本身不足以支持全面禁止。'),('个人自由的两个核心边界是什么？','参与者是理解风险的成年人，并且不使他人承担不合理危险。'),('培训要求和人数限额分别回应哪些问题？','培训回应挑战路线的能力要求；拥挤或救援容量不足时限额降低风险与公共压力。')],
'迁移到民用无人机：兼顾成年人的爱好选择与第三方安全，提出与风险相连的监管。','Adults should be free to enjoy flying drones, provided that they understand the risks and do not endanger others. Requiring training near crowded areas can address safety concerns more directly than a blanket ban. Limits may also be justified where emergency services need clear access.')
}
# Each phrase must be an exact substring after removing only Markdown emphasis.
# F = source material; C = corrected form; S = general supplement.
COLLOCATIONS={
'A1':[
('artistic potential','F','说明能力可能性：one’s artistic potential；potential表潜能通常不可数。','Schools can develop children’s scientific potential through practical experiments.'),
('a channel for','F','定义表达渠道：a channel for + 人 + to V，或for + N/V-ing。','Community meetings provide a channel for residents to discuss transport problems.'),
('a low barrier to entry','C','说明入门容易：a low barrier to entry；to是介词，entry为名词。','Free coding tools create a low barrier to entry for students with limited resources.'),
('a high level of technical skill','C','评价能力：a high level of + N；skill此处为能力总称。','Repairing medical equipment requires a high level of technical skill.'),
('extensive training','C','说明技能形成条件：undergo/receive + extensive training，training不可数。','Rescue workers need extensive training before attempting difficult operations.'),
('gains wide recognition','C','说明获得社会认可：work/achievement + gain(s) wide recognition。','A successful community recycling project may gain wide recognition.')],
'A2':[
('allow for self-expression','F','说明提供表达可能：allow for + N；区别allow sb to V。','Drama clubs allow for self-expression without requiring students to compete for grades.'),
('gain a better understanding of','F','写认知收益：gain a better understanding of + N/V-ing。','Studying abroad can help learners gain a better understanding of other cultures.'),
('distinctive character','C','说明整体特色：the distinctive character of + 地方/时期。','Local markets contribute to the distinctive character of a neighbourhood.'),
('making tangible improvements in','F','写切实改善：make tangible improvements in + 领域；正文为V-ing形式。','Reliable buses can make tangible improvements in rural residents’ daily lives.'),
('industrial design','F','说明产品外观与实用设计：industrial design；可作主语或介词宾语。','Industrial design can make household appliances easier for older people to use.'),
('complement scientific knowledge','C','说明补充而非替代：complement + N，不加with才接直接宾语。','Accounts from local residents can complement scientific knowledge of environmental change.')],
'A3':[
('investment in the arts','C','表达经费投入：investment in + 领域；避免art construction。','Investment in public transport can reduce dependence on private cars.'),
('allocated to public services','F','说明资金去向：funds be allocated to + N/V-ing；to为介词。','Additional resources could be allocated to supporting students with disabilities.'),
('maintaining mental well-being','C','说明心理收益：maintain + mental well-being；正文作V-ing并列成分。','Regular contact with friends can help people maintain mental well-being.'),
('reflect shared values','C','说明文化呈现作用：reflect + N；shared作定语。','Community celebrations can reflect shared values while welcoming newcomers.'),
('principle of diminishing returns','C','比较追加收益：the principle of + N；须补需求已较满足等条件。','The principle of diminishing returns may become relevant once basic classroom equipment is adequate.'),
('opportunities for cultural participation','C','说明资源保留的具体价值：opportunities for + N/V-ing。','Public libraries offer opportunities for independent learning to residents of all ages.')],
'B1':[
('channelled into road development','F','说明预算转向：money be channelled into + N/V-ing。','More funding could be channelled into improving bus reliability.'),
('city dwellers’ well-being','F','指出受益群体：群体所有格 + well-being；不是泛指everyone。','Affordable childcare can improve working parents’ well-being.'),
('removal of traffic bottlenecks','C','写具体改善措施：the removal of + 障碍名词。','The removal of unnecessary paperwork can shorten the application process.'),
('cultural identity','F','说明遗产对身份的意义：preserve/recognize + cultural identity。','Language teaching can help young people understand their cultural identity.'),
('capitalizing on','F','说明利用优势：capitalize on + N + to V；on不能省。','A rural school could attract visitors by capitalizing on its access to local wildlife.'),
('according to a strict set of criteria','F','说明决策依据：according to + N；criterion复数criteria。','Scholarships should be awarded according to a clear set of criteria.')],
'B2':[
('financially viable','F','检验能否负担实施：be financially viable；不同于effective。','A free meal programme may be financially viable if local suppliers offer stable prices.'),
('sedentary lifestyle','F','描述缺少活动的生活方式：a sedentary lifestyle；lifestyle可数。','Remote workers may develop a sedentary lifestyle unless they plan regular activity.'),
('ongoing maintenance costs','C','揭示持续成本：ongoing + maintenance costs；costs复数列支出。','Digital learning platforms also involve ongoing maintenance costs.'),
('discourage people from exercising regularly','C','解释行为障碍：discourage + sb + from + V-ing。','High fares may discourage families from visiting museums regularly.'),
('making time for','C','提出针对时间障碍的措施：make time for + N/V-ing。','Students can protect their health by making time for exercise during examination periods.'),
('warrants attention','F','说明问题值得重视：问题N + warrant(s) attention，不接to。','The loss of local languages warrants attention because it can weaken cultural continuity.')],
'B3':[
('on the periphery of the city','F','定位外围地区：on the periphery of + 地方。','Wildlife on the periphery of the city may lose habitat when new roads are built.'),
('spend less time travelling','C','说明时间收益：spend + 时间 + V-ing，不写on + 动词原形。','Online appointments allow patients to spend less time travelling to routine consultations.'),
('may have limited effects','C','限制效果判断：措施 + may have limited effects；不等于完全无效。','Lower tuition fees may have limited effects if students still cannot afford accommodation.'),
('have far-reaching effects','F','写广泛长远影响：政策N + have far-reaching effects；需具体解释影响。','Changes to teacher training can have far-reaching effects on classroom practice.'),
('the first being','F','列出多项之一：主句提到复数项目，the first being + N，独立主格。','Two barriers prevent enrolment, the first being the cost of transport.'),
('without sacrificing public green spaces','C','比较避免损失：without + V-ing + 宾语。','Digital services can improve access without sacrificing opportunities for face-to-face support.')],
'B4':[
('resides in the belief that','F','引出论证前提：justification + resides in the belief that + 完整从句。','The case for later school starts resides in the belief that rested students learn more effectively.'),
('giving rise to physical health problems','F','说明不良后果：give rise to + N；to为介词。','Unreliable transport can give rise to difficulties for workers on early shifts.'),
('available and accessible to','F','区分存在与真正可用：become/be available and accessible to + 人群。','Learning materials should be available and accessible to students with visual impairments.'),
('build a sense of community','F','说明互动的社会收益：build a sense of + N。','Shared gardening projects can build a sense of community among residents.'),
('provide shelter from bad weather','C','说明具体保护作用：provide shelter from + 风险/天气。','Covered bus stops provide shelter from bad weather for elderly passengers.'),
('in accordance with the needs','F','以需求为规划依据：in accordance with + N；正文needs补足指代。','Training should be provided in accordance with the needs of each department.')],
'T1':[
('gain a better understanding of the world','F','说明认知收益：gain a better understanding of + N。','Field trips can help children gain a better understanding of local agriculture.'),
('acquire knowledge systematically','F','说明系统学习：acquire + knowledge + systematically；knowledge不可数。','A structured apprenticeship helps trainees acquire knowledge systematically.'),
('impart the knowledge gradually, effectively, and systematically','F','说明教师传授方式：impart knowledge to + sb；三副词结构并列。','Mentors can impart practical knowledge gradually and systematically to new employees.'),
('lead a sedentary lifestyle','C','说明行为风险：lead + a/an + 形容词 + lifestyle。','Long hours of online work may encourage adults to lead a sedentary lifestyle.'),
('seek a compromise between','F','提出平衡：seek a compromise between + A + and + B；两项形式平行。','Cities must seek a compromise between visitor access and habitat protection.'),
('act with moderation','F','限制行为程度：act with moderation；with + 抽象名词。','Consumers can enjoy convenience foods while acting with moderation.')],
'T2':[
('having to compromise','C','表达不得不妥协：have to + V；compromise with sb on/over + N。','Shared housing can involve having to compromise with others over quiet hours.'),
('depending on their mood and preferences','F','说明选择依据：depending on + N；介词on不可省。','Learners can select an optional module depending on their interests and career plans.'),
('social contact and communication','C','说明互动渠道：social contact通常不可数，communication表交流不可数。','Community centres provide opportunities for social contact and communication.'),
('forge and strengthen bonds with others','F','说明关系形成与加深：forge/strengthen bonds with + 人。','Team projects can help students forge and strengthen bonds with others.'),
('meet their social needs','C','说明满足社交需求：meet + 所有格 + needs。','Older residents may meet their social needs through regular community activities.'),
('outweigh this disadvantage','F','回应权衡：benefits + outweigh + drawbacks，不加than。','The flexibility of online study may outweigh this disadvantage when reliable support is available.')],
'T3':[
('detrimental to children','F','表达不利影响：be detrimental to + N；to为介词。','Unpredictable schedules can be detrimental to family life.'),
('acts as a catalyst for','C','说明促进作用：act as a catalyst for + N/V-ing；a不可漏。','Affordable childcare can act as a catalyst for greater workforce participation.'),
('predispose some children to aggressive behaviour','F','表达倾向而非必然：predispose + sb + to + N/V-ing；some和may限制人群强度。','Repeated setbacks may predispose some learners to avoiding difficult tasks.'),
('as a means of imparting knowledge','F','表达教学工具：as a means of + V-ing；means单复数同形。','Museums can use interactive exhibits as a means of imparting knowledge.'),
('distinguish fiction from reality','C','说明辨别能力：distinguish + A + from + B。','Media lessons can help teenagers distinguish advertising claims from reliable evidence.'),
('the possible consequences of','C','让后果具体化：the possible consequences of + N/V-ing。','Applicants should consider the possible consequences of accepting an unpaid placement.')],
'C1':[
('place a premium on','F','说明高度重视：place a premium on + N/V-ing。','Schools should place a premium on feedback that students can understand.'),
('be in proportion to','C','说明分配相称：be in proportion to + N；be不可漏。','Training support should be in proportion to the difficulties employees face.'),
('on the basis of','F','说明评价基础：assess/decide + on the basis of + N。','Students should be assessed on the basis of their own work.'),
('assessed in terms of','C','说明评价维度：be assessed in terms of + N。','Transport projects should be assessed in terms of reliability as well as speed.'),
('factors beyond their control','C','区分责任与外部因素：factors beyond + 所有格 + control。','Farmers may suffer losses because of factors beyond their control.'),
('by no means guarantee success','F','限制必然推论：主体 + by no means guarantee(s) + N。','Expensive equipment can improve a laboratory but by no means guarantee success.')],
'C2':[
('weeks of annual leave','C','说明假期时长：数词 + weeks of annual leave；leave不可数。','A longer period of paid study leave may help nurses complete advanced training.'),
('rest and recharge themselves','F','解释恢复机制：rest and recharge (oneself)；反身代词与主语一致。','A quiet lunch area gives students a chance to rest and recharge themselves.'),
('give rise to stress','F','写压力原因：give rise to + N，to为介词。','Unclear examination instructions can give rise to stress.'),
('end up resigning','F','写最终行为后果：end up + V-ing，不接to V。','Students who receive no support may end up abandoning their courses.'),
('arrange cover in advance','C','提出提前替代安排：arrange cover；in advance作时间状语。','Hospitals can arrange cover in advance when staff attend training courses.'),
('provided that staffing and scheduling are properly managed','C','把可行性条件写明：provided that + 完整从句。','Flexible classes can improve access, provided that timetables are properly coordinated.')],
'C3':[
('in the interests of society as a whole','F','说明整体利益：in the interests of + 群体，不用interest单数表达此义。','Transport planning should operate in the interests of society as a whole.'),
('rests on providing safe food','C','写成功依赖的机制：rest on + N/V-ing；此处providing是V-ing。','The success of online learning rests on providing reliable feedback.'),
('in proportion to their efforts','F','说明报酬相称：in proportion to + N。','Scholarship support need not be in proportion to family income if the goal is equal access.'),
('taking a toll on the environment','F','说明损害：take a toll on + N，常含累积负面影响。','Repeated overnight work may take a toll on employees’ health.'),
('earn customer trust','F','说明责任经营回报：earn + 人群所有格/名词修饰语 + trust。','Clear assessment criteria can help schools earn parents’ trust.'),
('support business success','C','写社会与机构相互支持：support + N；须解释中间机制。','Reliable public transport can support business success by helping employees arrive on time.')],
'R1':[
('a deep sense of satisfaction','F','说明个人心理收益：a sense of + N；deep强化程度。','Completing a difficult project can give learners a deep sense of satisfaction.'),
('interpersonal skills','F','写能力收益：develop/improve + interpersonal skills，通常复数。','Group laboratory work can help students develop interpersonal skills.'),
('make community work mandatory for all','F','说明政策强度：make + N + mandatory for + 人群。','Making online registration mandatory for all may exclude residents without reliable internet.'),
('a moral obligation','F','区分道德责任与法律要求：a moral obligation to V。','Schools have a moral obligation to provide accessible learning materials.'),
('A better option would be to','F','提出替代措施：a better option would be to + V。','A better option would be to provide reliable buses before increasing parking charges.'),
('of their own volition','C','表示自愿：of + 所有格 + own volition；不是out of。','Students should be able to join debate clubs of their own volition.')],
'R2':[
('embark on their careers abroad','C','说明职业起步：embark on + N；on不可漏。','Cities may embark on ambitious recycling programmes when waste collection systems are reliable.'),
('places a premium on','F','说明社会重视：第三人称主语 + places a premium on + N。','An effective school places a premium on inclusive teaching.'),
('brain drain','F','描述技能外流：brain drain；避免与所有migration等同。','A region may experience brain drain when skilled workers lack career opportunities.'),
('bleak career prospects','F','解释流动动因：bleak + career prospects；prospects通常复数。','Young people facing bleak career prospects may seek further training.'),
('a blanket legal requirement','C','批评不分情形的强制：a blanket + legal requirement/restriction。','A blanket legal requirement to use digital services could disadvantage older residents.'),
('entice skilled professionals to stay or return','C','说明激励方向：entice + sb + to V；不能把流出作为留才目的。','Flexible schedules may entice experienced teachers to return to the classroom.')],
'R3':[
('a blanket ban','C','明确全面禁止力度：a blanket ban on + N/V-ing。','A blanket ban on all mobile devices may remove useful learning tools.'),
('a high level of risk','F','说明风险程度：a high level of + risk；需给具体风险。','Working without protective equipment can involve a high level of risk.'),
('safeguarding people’s well-being','F','说明保护责任：safeguard + N；正文为V-ing。','Housing standards can play a role in safeguarding tenants’ well-being.'),
('provided that the ban was effectively enforced','C','交代效果依赖执行：provided that + 完整从句；enforce是执行。','Parking restrictions could reduce congestion, provided that they were consistently enforced.'),
('allowing informed choices despite some risk','C','提炼有条件原则：allow + N；despite + N。','Patient education can support informed choices despite some uncertainty.'),
('minimum training requirements','C','提出能力门槛：meet + minimum training requirements。','Laboratory assistants should meet minimum training requirements before handling hazardous substances.')]
}
CORRECTION_META={
'A1':[('区分创作与广泛认可','a truly generally recognized product','gains wide recognition',3),('工具与创作行为匹配','conducting the art creation','create art freely',1),('解释现象不等于证明正当','That justified the status quo','This helps to explain why',3)],
'A2':[('表达之后补受众理解','','what experiences such as joy or loss feel like from the inside',1),('修正词性并限制艺术科学对立','art brings aesthetics while science brings functional','reveals the aesthetic value of everyday life',2),('撤去未经支持的人物因果','','not only on its operating system but also on its industrial design',2)],
'A3':[('预算投入不机械译为建设','art construction','investment in the arts',0),('比较紧迫性而非否认文化需求','live and travel as normal people','live more independently and travel with fewer barriers',1),('收益递减需要前提','','once essential public service needs have been met',3)],
'B1':[('统一指代与虚拟条件','Will future generation','Would future generations',2),('具体城市改为假设场景','','A city, for example, could preserve an old temple',2),('道路收益递减加适用条件','','where road infrastructure is already well developed',3)],
'B2':[('运动与维护费搭配校正','consistent maintenance costs','ongoing maintenance costs',2),('预算有限不等于政策必败','','may have limited scope to increase',2),('空间与时间障碍可以并存','','not simply the lack of outdoor activity space but also a heavy workload or study burden',3)],
'B3':[('新增住宅须可负担且靠近工作','would be afforded to','provided these homes were affordable and close to their workplaces',1),('承认距离并回应最佳方案','','overlooks other important causes of long commuting times',2),('搬迁须接近员工住处','','provided this brings them closer to where their employees live',3)],
'B4':[('保留正式结构并补费用门槛','','low-cost sports facilities',1),('运动含义与并列句修整','taking a brisk stroll','taking a brisk walk',1),('天气优势与数量要求不夸大','','their indoor areas can also provide shelter from bad weather',2)],
'T1':[('纪录片与嵌入问句','what is pollination','what pollination is',2),('学习机会增加与替代教学分开','','provided that suitable content were selected',1),('健康风险与结论条件化','','may cause eye strain',3)],
'T2':[('代词与散步搭配修正','talking for a walk','taking a walk',2),('偏好冲突中一方可能妥协','','one of them may end up watching a less preferable film',1),('日常社交补偿需要条件','','when they maintain other shared activities',3)],
'T3':[('冠词及视为结构修正','','acts as a catalyst for',0),('健康与行为影响避免绝对化','','may cause eye strain',1),('成人讨论提供模仿风险干预机制','','distinguish fiction from reality',3)],
'C1':[('薪酬句法与自然搭配','','should be in proportion to performance or contribution',0),('高薪依据限定自身责任贡献','','their decisions can affect the productivity of an entire workforce',2),('约定工资不推出绩效奖金合理','','still receive their agreed salary',3)],
'C2':[('为至少四周补持续恢复理由','','a two-week break for sustained recovery',2),('可行性靠错峰代班而非善意','','arrange cover in advance',3),('年假不可数并收敛断言','Lengthened','An extended holiday',2)],
'C3':[('责任及指代搭配修整','carry out responsibility','fulfil their social responsibilities',1),('具体公司改为假设及安全食品','','providing safe food',1),('自愿捐助与外部损害分开','Probably not','such damage imposes costs on others',2)],
'R1':[('志愿与自愿固定搭配','out of volition','of their own volition',3),('人数不等于专业服务能力','','require relevant experience or qualifications',2),('直接比较全面强制的额外得失','','voluntary participation can retain many of the gains',3)],
'R2':[('职业价值与吸引方向校正','entice the exodus','entice skilled professionals to stay or return',3),('培训国不同于国籍国','','public investment in these disciplines can pay off more directly',1),('道德义务不足以支持法律强制','','a moral obligation alone does not justify compelling people to stay',3)],
'R3':[('危险运动与资质搭配修正','a minimum of qualification','minimum training requirements',3),('禁令效果须依赖执行','','provided that the ban was effectively enforced',1),('知情选择、救援与监管边界','','risks to rescuers and demands on public resources',3)]
}
TOPICS={'A':('艺术','Art'),'B':('建筑与城市','Buildings and Cities'),'T':('电视与教育','Television and Education'),'C':('企业与工作','Business and Work'),'R':('权利与责任','Rights and Responsibilities')}
for record in records:
    code=record['code']; englishTitle,taskType,position,notes,qa,transfer,transferAnswer=DETAILS[code]
    topic,topicEn=TOPICS[code[0]]
    record.update(englishTitle=englishTitle,topic=topic,topicEn=topicEn,type=taskType,position=position,paragraphNotes=[note(*n) for n in notes],questions=[q for q,a in qa],answers=[a for q,a in qa],transfer=transfer+'（迁移答案为自拟。）',transferAnswer=transferAnswer)
    assert len(notes)==len(record['essayParagraphs']),(code,len(notes),len(record['essayParagraphs']))
    plain='\n\n'.join(record['essayParagraphs']).replace('**','')
    record['collocations']=[]
    for phrase,source,usage,example in COLLOCATIONS[code]:
        assert phrase in plain,(code,'collocation missing',phrase)
        record['collocations'].append(dict(phrase=phrase,source={'F':'熟悉（讲义）','C':'校正','S':'通用补充'}[source],usage=usage+' 跨题例句为自拟，不是讲义原句。',example=example))
    for correction,meta in zip(record['corrections'],CORRECTION_META[code]):
        title,original,revised,anchor=meta
        assert revised in plain,(code,'revised quote missing',revised)
        assert revised in record['essayParagraphs'][anchor].replace('**',''),(code,'anchor mismatch',anchor,revised)
        correction.update(title=title,original=original,revised=revised,paragraphIndex=anchor)
    assert len(record['questions'])==len(record['answers'])==3
    assert all(2<=len(n['chain'])<=5 for n in record['paragraphNotes'])
assert len(records)==16
output=ROOT/'data/five.json'
output.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
# Exact comparison against source delimiters, including emphasis and paragraph order.
for i,(record,h) in enumerate(zip(json.loads(output.read_text()),heads)):
    end=heads[i+1].start() if i+1<len(heads) else text.index('**这批文章最值得继续沿用的写法**')
    section=text[h.end():end]
    original=section.split('**小修版**',1)[1].split('**最值得理解的三处调整**',1)[0].strip()
    assert '\n\n'.join(record['essayParagraphs'])==original,record['code']
    actual=len(record['essayParagraphs'])
    print(record['code'], 'paragraphs=',actual,'collocations=',len(record['collocations']),'corrections=',len(record['corrections']),'declaredWords=',record['declaredWords'])
print('Verified records:',len(records),'paragraphs:',sum(len(r['essayParagraphs']) for r in records),'corrections:',sum(len(r['corrections']) for r in records),'collocations:',sum(len(r['collocations']) for r in records),'recall pairs:',sum(len(r['questions']) for r in records),'exact source mismatches: 0')
