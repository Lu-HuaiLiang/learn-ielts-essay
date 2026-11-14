"""Build all eight-topic study records while preserving source Markdown verbatim."""
import re, json
from pathlib import Path
from difflib import SequenceMatcher
ROOT=Path('/Users/andy.lu/🟢learn-something/learn-ielts-essay')
REF=Path('/Users/andy.lu/Documents/Codex/2026-10-17/ke/work/skills/write-ielts-essays-my-style/references')
s=(ROOT/'materials/eight-topics.md').read_text()
records=[]
for m in re.finditer(r'^### ([A-Z]+\d+) (.+?)｜(\d+)词\n(.*?)(?=^### |^## |\Z)',s,re.M|re.S):
    code,title,words,body=m.groups()
    topic=list(re.finditer(r'^## (\S+) (.+)$',s[:m.start()],re.M))[-1].groups()
    essay=body.split('**小修版（加粗处为改动）**')[1].split('**最值得理解的调整**')[0].strip()
    cb=body.split('**最值得理解的调整**')[1].strip().removesuffix('---').strip()
    corrections=[]
    for c in re.finditer(r'\d+\. 原文：`(.*?)`\s+修订：`(.*?)`\s+(.*?)(?=\n\d+\. 原文|\Z)',cb,re.S):
        original,revised,expl=c.groups()
        corrections.append(dict(title='',original=original,revised=revised,explanation=expl.strip(),paragraphIndex=-1))
    records.append(dict(id='eight-'+code.lower(),code=code,title=title,englishTitle='',topic=topic[1],topicEn=topic[0],sourceGroup='eight',sourceHeading=m.group(0).splitlines()[0],declaredWords=int(words),question='\n'.join(x[2:] for x in body.splitlines() if x.startswith('> ')),essayParagraphs=essay.split('\n\n'),type='',position='',paragraphNotes=[],corrections=corrections,collocations=[],questions=[],answers=[],transfer='',transferAnswer=''))
D={}
def add(code,title,typ,pos,notes,corrections,collocations,qa,transfer,example):
    D[code]=dict(englishTitle=title,type=typ,position=pos,notes=notes,correctionMeta=corrections,collocationData=collocations,qa=qa,transfer=transfer,transferAnswer=example)
# Notes are role, paragraph-specific explanation, explicit stages. Examples are newly authored.
add('W01','Conserving Drinking Water','原因与措施双问','可饮用水减少主要源于生产污染与生活浪费；政府监管排污，个人减少浪费并安全复用水。',[
('开头：两因两策','先明确减少的是可安全饮用的水，再分别提出污染和浪费；政府与个人共同参与，为后文分工做准备。',['饮用水可用量下降','生产污染＋生活浪费','政府监管＋个人节水']),
('原因：生产污染与浪费累积','人口增加推动食品和衣物生产，化学品进入水道使水无法饮用；刷牙不关水龙头则以人口规模把小浪费累积为供应压力。',['人口增长带动生活品需求','生产排放污染水源','安全饮用水减少','大量微小浪费进一步压低供应']),
('措施：逐项对准原因','工业监管同时抓用水效率和污染处罚，排放标准要求废水先处理；个人用洗菜水浇植物、刷牙关水龙头，对应复用和减量。',['政府规范生产并处罚污染者','废水处理达到排放标准','个人适当复用并关水龙头','污染和无效耗水共同减少']),
('结尾：措施回扣','结尾重申污染与浪费两条原因，回收监管执行和生活减量；could保留严重后果的可能性，而非保证灾难发生。',['污染＋浪费导致短缺','执行监管＋减少日常浪费','不行动可能加重后果'])],
[('物品类别与污染主体',1),('人口规模怎样放大浪费',1),('结尾与措施一致',3)],
[
('the foremost of which are','列出主要原因：reasons, the foremost of which are + 复数名词。','School dropout has several causes, the foremost of which are financial pressure and inadequate support.'),
('The sheer size of the population','说明微小行为的规模效应：the sheer size of + 群体名词。','The sheer size of the population means that small energy savings can add up.'),
('impose sanctions on','处罚对象：impose sanctions on + 违规者；区别于执行规则。','Authorities could impose sanctions on companies that mislead consumers.'),
('meet wastewater discharge standards','达到标准：meet + 标准名词；本篇宾语限定废水排放。','Training providers should meet quality standards before receiving public funds.'),
('enforcing regulations','落实规则：enforce + regulations；此处including后用V-ing。','Enforcing regulations on misleading claims can help protect young consumers.')],
[('食品和衣物怎样使饮用水减少？','需求上升带动生产，生产排放化学品或农药进入水道，使可安全饮用的水量减少。'),('为什么单次刷牙浪费很少，仍值得写？','人口众多使微小浪费累积，进一步增加淡水供应压力。'),('政府与个人各采取哪两类行动？','政府提高工业用水效率并处罚污染排放；个人复用适当水源并减少日常浪费。')],
'换成家庭能源浪费，写两三句，保留“小浪费—人口累积—个人减量”的机制。','Leaving lights on in an empty room may seem insignificant, but the sheer size of the population can turn this habit into substantial energy waste. Individuals can help by switching off unused appliances and choosing efficient lighting.')
add('W02','Regulating Freshwater Use','双边讨论与个人观点','保障基本用水权，同时监管超额使用；阶梯水价用不同单价协调两者。',[
('开头：区分权利范围','呈现自由使用与政府限制的分歧，并立即限定作者立场：保护基本需求，不承诺无限用水。',['个人主张自由用水','政府主张资源保护','保障基本需要并管控超额用量']),
('一方：共享资源与付费使用','先以共享自然资源说明自由使用的理由，再提出承担处理和运输成本的条件；From this perspective提示这是支持者的视角。',['水被视为共享资源','无主体独占','支持自由满足生活与商业需要','使用者承担处理运输成本']),
('另一方：有限资源与累积外部影响','明知水有限仍有小额浪费，人口规模让其累积为耗减，可能波及当代与后代，因此引出政府保护公共利益的责任。',['个体浪费看似微小','人口规模放大总浪费','淡水耗减影响多代人','政府有公共管理理由']),
('个人观点：阶梯水价的机制','关键不是笼统折中，而是基本用量低价、超额部分高价；高边际价格鼓励少浪费，同时保留满足基本需求的入口。',['基本需求用量低价','超额消费单价提高','降低过度用水动机','基本获取得到保护','资源耗减放缓']),
('结尾：两目标同一措施','用基本权利与超额监管重申答案，并再次指出阶梯水价协调两目标，避免回到无限使用权。',['承认基本用水权','限制过度消费','阶梯水价协调需求与保护'])],
[('用资源共享替代循环论证',1),('当代与后代都可能受影响',2),('基本用水权与无限使用不同',4)],
[
('giving priority to','表达优先顺序：give priority to + N/V-ing；不等于排除其他目标。','Schools should give priority to helping pupils who lack basic literacy skills.'),
('lay exclusive claim to','主张独占：lay exclusive claim to + 资源/成果；本篇为观点转述。','No department should lay exclusive claim to a shared training budget.'),
('the depletion of fresh water','资源耗减：the depletion of + 资源名词。','The depletion of natural habitats can threaten local wildlife.'),
('providing an incentive to reduce excessive use','措施产生行为激励：provide an incentive to + V；providing补充结果。','A small reward can provide an incentive to return reusable containers.'),
('without restricting access to water for basic needs','说明兼顾条件：without + V-ing；restrict access to + N。','Cities can discourage unnecessary car journeys without restricting access to essential services.')],
[('自由用水的一方怎样避免“有权所以有权”的循环？','先提出水是共享自然资源的理由，再说明使用者付处理和运输费用的自由使用主张。'),('阶梯水价怎样同时照顾个人与公共利益？','基本需求部分收费较低，超额部分收费较高，以价格激励减少过度使用。'),('本文结尾为何不能写as much as they want？','该说法承诺无限用水，与限制超额用量的主体段和作者立场矛盾。')],
'换成城市道路收费，写两三句，说明如何保护必要出行并抑制过度用车。','Road charges could be lower for essential journeys and higher for repeated discretionary trips at peak times. This would provide an incentive to reduce unnecessary driving while protecting access to basic services.')
add('TE01','Remote Work and Its Trade-offs','利弊权衡（outweigh）','在定期面对面交流等支持下，日常节省的通勤时间和办公成本总体超过部分自发互动的损失。',[
('开头：群体收益与整体判断','先承认同事互动不足，再按员工和公司列出两种受益，为后文分别解释时间和成本做好安排。',['远程工作扩大','互动机会减少','员工时间＋企业成本收益','总体利大于弊']),
('员工收益：时间重新分配','would otherwise指出本来消耗于通勤的时间；省下时间用于休息与陪伴家人，才落到幸福感，而非只停在方便。',['免去日常通勤','腾出可支配时间','用于休息或家人','幸福感改善']),
('企业收益：成本转成竞争力','减少场地需求降低租购办公室及相关开销；将节余投向人力和软件，才解释为什么初创企业尤其受益。',['办公空间需求下降','场地开销减少','节余投入人力与软件','企业竞争力提升']),
('弊端与缓解：同事支持','缺少日常连接伤害团队合作，新人又更难观察学习；定期见面加强联系只能部分缓解，不能保证完全恢复。',['接触同事机会减少','合作与新人学习受阻','同伴支持不足','定期面对面会议增进联系']),
('结尾：给出权衡依据','With such support回指前段会议支持，用每天持续获得的时间和成本收益，对比仍会丧失的部分自发互动机会。',['承认沟通代价','配套会议缓解部分问题','每日节省时间与成本','总体收益更大'])],
[('减少而非取消办公场地',2),('companies与their一致',2),('面对面表达与同事支持',3)],
[
('would otherwise be spent','机会成本：time/money that would otherwise be spent on + N/V-ing。','Money that would otherwise be spent on printed manuals could fund teacher training.'),
('cover the overhead costs','承担经常性开销：cover + costs；overhead修饰间接运营成本。','Small museums may struggle to cover the overhead costs of maintaining their buildings.'),
('take a heavy toll on','说明严重负面影响：take a heavy toll on + 人/状态/活动。','An excessive exam workload can take a heavy toll on students’ well-being.'),
('communicate face to face','说明沟通方式：communicate + face to face；名词前用face-to-face。','Language learners can build confidence when they communicate face to face with visitors.'),
('forge bonds','建立关系：forge bonds with + 人 / between + 双方。','Community sports can help residents forge bonds with their neighbours.')],
[('节省通勤时间后，如何把论证推进到幸福感？','腾出的时间可用于休息和家人，改善工作与生活平衡，进而提高幸福感。'),('为什么少租办公室能提升竞争力？','节省场地相关开销后，可以把资金重新投入人力和软件。'),('结尾用什么依据说明outweigh？','定期会议部分补足联系后，每日持续的时间和成本收益超过部分自发互动的损失。')],
'换成在线教育，用两三句讨论时间收益及同伴交流代价，并给出一个配套条件。','Online classes save time that would otherwise be spent travelling to campus, allowing students to review difficult material. They may also reduce informal peer contact, so regular discussion groups are needed to help learners forge bonds.')
add('TE02','Robots at Work and Home','积极或消极发展判断','总体积极：工作效率与家务减负值得支持，但必须帮助岗位被替代者培训并重新就业。',[
('开头：判断与代价范围','把机器人收益分为职场效率和家庭家务，同时把失业风险限定在部分行业，避免从岗位替代推成社会大失业。',['机器人改变工作生活','效率提升＋家务减少','部分行业岗位损失','总体积极']),
('收益：同一技术的两类场景','仓库机器人分拣搬运货物推动业务效率；扫地机器人接管清洁任务，两个实例都切合机器人而非任意自动化家电。',['仓储机器人高效分拣搬运','支持网购业务','扫地机器人承担清洁','人们减少重复劳动与家务']),
('代价与措施：替代到再就业','制造业重复岗位更可能被替代，影响劳动者生计；培训针对受影响的人，让技能适应更重知识的行业需求。',['重复任务被机器人承担','部分工人失去岗位和收入','再培训与技能升级','为转岗重新就业做准备']),
('结尾：有条件的总体支持','provided that不是装饰，明确总体积极判断以失业问题得到支持为条件；结尾把拓技能落到找到新工作。',['企业效率与家庭减负','承认受影响工人困难','协助拓展技能并找新工作','满足支持条件后总体积极'])],
[('机器人实例要切题',1),('岗位替代不等于大规模失业',2),('培训主体与就业目标明确',3)],
[
('providing a helping hand','说明辅助作用：provide a helping hand for + 群体 / in + V-ing。','Public libraries are providing a helping hand for adults learning digital skills.'),
('domestic chores','家务劳动：escape from / spend time on + domestic chores。','Shared housing arrangements can help students divide domestic chores fairly.'),
('can displace workers','限定就业影响：can displace workers in + 行业/岗位。','A shift towards online retail can displace workers in traditional shops.'),
('boost operational efficiency','提升运行效率：boost + efficiency；须说明靠哪一环节。','A shared booking system can boost operational efficiency in sports centres.'),
('provided that','给判断附条件：provided that + 完整从句。','Tourism can benefit a village, provided that visitor income supports local conservation.')],
[('为什么家务例子改成扫地机器人？','机器人题应举机器人；普通自动化家电未必属于机器人，扫地机器人类别明确。'),('就业链中哪一步让培训具有针对性？','重复岗位被替代后，受影响工人缺少新岗位技能，培训帮助他们适应需求并重新就业。'),('结尾provided that限定了什么？','只有失业问题得到支持、工人能够拓宽技能和找新工作，作者才给出总体积极评价。')],
'换成商店采用自助结账，写两三句把效率提升与员工转岗支持结合。','Self-service checkouts can boost operational efficiency by handling routine payments. This can be a positive change, provided that affected employees receive training for customer support or stock management roles.')
add('T01','Fuel Prices and Congestion','同意程度题（评估best）','提高油价可能有用，但在缺少替代交通时效果有限；改善公交与道路瓶颈更直接。',[
('开头：有用不等于最佳','题眼是best，因此承认油价有部分作用后，转向它未解决用车必要性的局限，而非声称涨价完全无效。',['提议涨油价治堵','承认一定效果','未解决用车必要性','寻找更有效替代']),
('让步：价格如何影响行为','收入提升让车买得起，便利偏好让车更吸引人；油价提高可能促使减少开车或改乘公交，继而减少路上汽车。',['收入与便利偏好增加用车','拥堵损害通勤者','油价上涨改变部分出行选择','汽车减少缓解拥堵']),
('反驳：两个前提未必成立','政策需要司机看重油费且有可行替代；但舒适便利、公交缺失可能压过价格变化，养车成本本已不止燃油。',['把选择主要归于油费','假定公交替代可行','部分司机重便利或缺少替代','单独涨油价不足以改变选择']),
('替代：针对选择与瓶颈','公交扩容、延伸和规划改善实际便利，降低驾驶必要性；在车辆少却仍堵的地方，针对道路瓶颈施工比一味改价格更对症。',['公交运力路线服务改善','吸引自愿改乘','针对瓶颈改善道路','分别减少车辆与局部堵塞']),
('结尾：条件式比较','用缺少合适替代这一条件限制涨价效果，再以公交网络和道路设计对应替代方案，回答为什么不是最佳。',['无替代时油价作用有限','改善公交与路网设计','更直接缓解拥堵'])],
[('可行替代方式的行为前提',2),('自愿换乘的主语与可能性',3),('条件效果替代必败判断',4)],
[
('the pursuit of convenience','解释偏好动机：the pursuit of + 抽象目标；不等于收入能力。','The pursuit of convenience may encourage shoppers to choose home delivery.'),
('opting for another affordable mode of transport','选择替代：opt for + N；opting为与reducing并列的V-ing。','Parents may respond to high fees by opting for a community childcare scheme.'),
('the questionable assumption that','指出可疑前提：be based on the questionable assumption that + 从句。','The policy rests on the questionable assumption that every student has a quiet room.'),
('may be less responsive to fuel prices','说明较弱反应：be responsive to + N；less不等于完全不反应。','Experienced employees may be less responsive to small financial bonuses.'),
('may voluntarily shift','行为转变：may voluntarily shift from + 起点 + to + 终点。','With affordable local facilities, families may voluntarily shift from indoor entertainment to outdoor activities.')],
[('best与effective有何区别？','有效只说明能产生作用；最佳还要与替代方案比较效果和可行性。'),('涨油价要改变出行依赖哪两个前提？','司机的选择主要受燃油成本影响，且他们有可行的非私车替代方案。'),('公交改善与道路改善分别解决什么？','公交运力路线解决驾驶必要性和便利不足；针对性道路改造缓解局部瓶颈。')],
'换成提高游戏价格减少沉迷，写两三句先承认可能有效，再指出行为前提并给出更直接措施。','Higher game prices may discourage some purchases, but this assumes that spending is the main reason people keep playing. Limits on play time and attractive offline activities may address excessive gaming more directly.')
add('T02','The Benefits of a Vehicle-free Day','利弊权衡（题面另附同意程度问法）','在运力配套充足时，无车日的治堵减排和长期体验收益超过服务投入成本。',[
('开头：定义与实施条件','按题面保留公交、自行车和出租车通行，不把无车日误读为所有车辆禁行；总体支持取决于足够替代运力。',['私车增长增加拥堵污染','指定车辆外限制市中心通行','需要公交运力承接','总体收益较大']),
('即时收益：车辆减少','车辆排队占用道路且尾气污染空气；减少车辆直接降低这两种负担，健康只写潜在风险，不断言具体疾病。',['车辆拥堵道路','尾气带来污染风险','限制车辆数量','交通与空气压力下降']),
('长期收益：体验改变偏好','被促使改乘公交的人通过亲身体验认识潜在省钱省时和减排收益；只有体验足够好且降低后续用车依赖，才有长期作用。',['活动推动更多人尝试公交','亲身认识潜在优势','绿色出行意识增强','可能持续减少私车依赖']),
('弊端、配套与成本理由','客流突增若运力不跟上会让公交变得不吸引人，甚至活动后更依赖私车；追加预算扩容可缓解，且日常乘客继续受益使投入更合理。',['活动客流骤增','运力不足损害体验','追加预算提供足够服务','额外运力活动后仍服务乘客']),
('结尾：以持续收益权衡','不是因为治堵迫切就推出必须实施，而是比较交通污染收益与扩容成本，突出新增运力的日常价值。',['治堵减排收益','承担服务改善成本','日常乘客持续受益','可考虑定期举办'])],
[('健康风险避免具体疾病强因果',1),('直接体验与名词并列',2),('回答权衡而非只说需求迫切',4)],
[
('act as a catalyst for','催化变化：act as a catalyst for + N/V-ing。','A community festival can act as a catalyst for interest in local history.'),
('through direct experience','说明认识来源：learn/recognise + 宾语 + through direct experience。','Students can understand workplace expectations through direct experience.'),
('reduces their dependence on private cars','降低依赖：reduce dependence on + N。','Practical cookery lessons may reduce students’ dependence on ready-made meals.'),
('increasing budget allocation','具体投入方式：increase budget allocation to + V / for + N。','Increasing budget allocation for mentoring could improve support for new teachers.'),
('helping to justify its cost','提供成本合理性：help to justify + cost；helping为结果补充。','A shared hall can serve both classes and local events, helping to justify its cost.')],
[('无车日为什么可能产生超出一天的效果？','良好公交体验可能改变偏好，增强绿色出行意识，使人以后减少对私车的依赖。'),('运力不足怎样反而削弱活动目的？','客流增加使服务体验变差，人们不再认为公交吸引人，活动后可能更依赖私车。'),('为什么额外服务费用可能值得承担？','新增运力不仅服务活动当天，也持续惠及日常乘客，使投入产生长期价值。')],
'换成学校免费运动体验日，写两三句说明亲身体验如何改变参与偏好及怎样处理配套不足。','A free sports day can encourage pupils to recognise the benefits of exercise through direct experience. Schools should provide enough instructors and equipment, since overcrowded sessions may discourage later participation.')
add('T03','Free Public Transport Around the Clock','同意程度题（评估best）','免费与全天服务有部分价值，但对部分司机吸引力不足、夜间需求与高峰错位；针对性改善更具成本效益。',[
('开头：拆分效果与可行性','承认全天免费公交能够帮助部分乘客，再从效果和可行性评价best，为分别分析免票与夜班铺路。',['提出24/7免费政策','承认可能有用','比较效果与可行性','不认同最佳方案']),
('免票局限：便利前提','部分车主接受私车更高费用来换舒适便利；若公交本身不便，去掉票价也未必促使其改乘。',['政策假定票价影响很大','部分车主优先考虑便利','公交不能提供可比便利','单纯免票吸引力有限']),
('全天局限：时段与成本','夜间增班可能满足夜间出行，却不直接增加早高峰运力；低夜间需求下还需支付非正常时段加班成本，预算理由不足。',['夜间增班服务夜间需求','难直接缓解高峰拥堵','非正常时段工资提高运营成本','低需求地区投入难证明合理']),
('替代：按需求改善','把服务延伸限定在需求高的地点或时段，并改善容量路线；再改造具体道路瓶颈，使预算直接对准拥堵原因。',['需求高处扩容延伸服务','提高公交便利吸引转乘','针对道路瓶颈施工','减少高峰与局部堵塞']),
('结尾：成本效益比较','同时承认部分乘客受益，保留对部分司机作用有限的范围；用潜在成本对照针对性改善，避免判定整个政策必败。',['部分乘客受益','部分司机不转乘','全天服务可能成本高','针对性改善更具成本效益'])],
[('服务不便条件下效果有限',1),('夜间与高峰错位及between搭配',2),('以成本效益回答best',4)],
[
('give relatively little weight to fares','说明考虑权重：give little weight to + N；不是完全忽视。','Employers may give relatively little weight to grades when applicants have strong practical experience.'),
('in exchange for comfort and convenience','交换关系：accept/pay + 成本 + in exchange for + 收益。','Some tourists pay higher prices in exchange for more personalised guidance.'),
('may do little to relieve peak-hour congestion','限定作用：do little to + V，表示作用小而非完全无效。','Extra homework may do little to improve understanding when students receive no feedback.'),
('place additional pressure on','增加负担：place pressure on + 承受者；additional修饰pressure。','Rising rents can place additional pressure on small cultural organisations.'),
('less cost-effective than targeted improvements','成本效益比较：be less cost-effective than + N/V-ing。','A universal subsidy may be less cost-effective than targeted support for disadvantaged learners.')],
[('为什么免票未必让车主改乘？','有些车主本已接受更高成本换便利舒适；公交服务不便时票价不是决定因素。'),('夜间增班与治堵之间缺哪一步？','它没有直接增加高峰期服务，夜间需求与主要拥堵时段错位。'),('结尾为何不能写surely a recipe for failure？','局部吸引力有限和潜在高成本只能支持比较性判断，不能证明所有收益为零或必然失败。')],
'换成学校图书馆全天免费开放，写两三句把低夜间需求与更有针对性的学习支持比较。','Keeping a school library open all night may do little to help students who need guidance after class. Where overnight demand is low, afternoon tutoring could be more cost-effective than continuous staffing.')
add('F01','A Blanket Ban on Unhealthy Food','同意程度题（全面禁售）','承认限制购买可能改善健康，但缺乏便利健康替代品和经济转型时间时，全面禁售未必可行。',[
('开头：评价全面禁令','承认健康目标，反对的是一刀切的实施方式；按个人日常需要和经济影响两方面评估可行性。',['过量摄入带来健康风险','提出全面禁售','承认可能健康收益','质疑个人与经济可行性']),
('让步：购买入口与摄入','便利购买可能促成不健康习惯；禁售限制渠道后，顾客可能改买健康产品，继而减少过量摄入相关风险。',['便宜易得的高热量高糖产品','不健康习惯与过量摄入风险','禁售限制购买渠道','可能转向健康产品并降低风险']),
('个人局限：替代品必须可用','忙碌消费者需要省下做饭时间，部分方便食品受禁后，健康替代若既不便又贵，就难满足日常需要；预制不自动等于有害。',['快节奏生活产生便利需求','部分人依赖预制食品','同等便利廉价替代不足','全面禁售妨碍日常需要']),
('经济局限：调整成本','食品供应链和餐饮提供就业与税收，全面禁售冲击相关企业和工人；尤其没有适应时间时成本更大，不能只笼统说经济不好。',['食品销售产生税收','供应链餐饮提供就业','禁令影响相关业务','缺乏适应时间加重企业工人损失']),
('结尾：回扣实际需求','总结健康风险存在，但消费需求与经济成本使禁令并非总可行；没有新增多数人适量食用这样的未经论证理由。',['承认过量摄入风险','考虑消费者实际需要','考虑经济调整成本','不支持一概禁售'])],
[('access与结果分词并列',1),('预制类别不等于有害配料',2),('结尾不得新增多数人适量断言',4)],
[
('a blanket ban on','全面禁令：impose a blanket ban on + N/V-ing；范围强，需相称理由。','A blanket ban on school trips could deprive pupils of valuable learning experiences.'),
('customers’ access to these products','资源渠道：restrict + 人’s access to + N。','High ticket prices can restrict families’ access to cultural events.'),
('is grounded on the premise that','指出论证前提：be grounded on the premise that + 完整从句。','The proposal is grounded on the premise that every household has reliable internet.'),
('generates tax revenue','经济收益：generate tax revenue from + 销售/活动。','A well-managed tourism sector generates tax revenue that can support local services.'),
('given consumers’ practical needs','给判断理由：given + N；相当于考虑到该因素。','Given students’ practical needs, evening transport services deserve attention.')],
[('禁售改善健康的完整链条是什么？','限制购买入口，鼓励转向健康替代品，可能减少过量摄入带来的风险。'),('为什么不能把预制食品或添加剂直接等同于有害食品？','预制描述加工方式，添加剂是不同配料类别，是否有害不能从类别本身推出。'),('反对全面禁售的两项主体理由是什么？','一些消费者缺少同样便利且可负担的健康替代品；相关企业工人可能承担税收就业及转型冲击。')],
'换成全面禁止市中心私车，写两三句先承认环境收益，再检查替代出行和适应时间。','A blanket ban on private cars could reduce traffic emissions. However, residents need affordable alternative transport, and local businesses may require time to adjust their deliveries before such a policy becomes viable.')
add('F02','Raising the Price of Sugary Products','同意程度题（普遍涨价）','涨价可能减少过量摄入，但对适量者增加支出；本文偏好清楚标签帮助消费者知情选择。',[
('开头：区分目标与工具','公共健康目标正当不自动证明所有含糖产品都应涨价；作者针对政策过宽，而非否认过量摄入的风险。',['过量糖摄入可能危害健康','提出降低可负担性','健康目标可以理解','普遍涨价范围过宽']),
('让步：价格到健康的中间步骤','涨价先影响购买可能性，再影响摄入量，最后才可能降低相关风险；连续might与could让假设链保持一致。',['价格提高','购买可能性下降','摄入量可能减少','相关健康风险可能降低']),
('反对：适量者的额外成本','把风险中心定位于过量摄入，再承认一些人适量享用舒适食品；这些人会多花钱，却未必改变已经合理的摄入。',['问题集中在过量摄入','部分消费者已适量食用','涨价仍覆盖这些消费者','增加支出却未必改善其行为']),
('替代：提供信息而非普遍加价','借包装警示原则提出糖含量分级标签，让过量消费者认识风险并有据选择；这是拟议方案而非未经核实的国家政策事实。',['清楚标示含糖量等级','消费者认识风险','更知情地选择与控制摄入','避免所有消费者成本上升']),
('结尾：针对性判断','保留价格可能有用的让步，再回到已适量者成本与标签的信息作用；清楚表达偏好标签，未宣称标签保证效果。',['涨价或有健康作用','适量者仍承担成本','标签支持知情选择','偏好更有针对性的方案'])],
[('价格用raised并保持条件结果一致',1),('限定适量者与具体支出',2),('政策事实改成假设标签方案',3)],
[
('associated with excessive sugar consumption','关联而非确证唯一因果：be associated with + N/V-ing。','Long journeys may be associated with fatigue and reduced family time.'),
('in moderation','限定程度：consume/use/enjoy + N + in moderation。','Digital entertainment can be enjoyable when used in moderation.'),
('facing a heavy workload','说明负担情景：face a heavy workload；workload为可数负担量。','Teachers facing a heavy workload may need more administrative support.'),
('do not, by themselves, justify','区分问题与措施合理性：X do not, by themselves, justify + N/V-ing。','Occasional delays do not, by themselves, justify closing an entire railway line.'),
('help consumers make informed choices','信息支持：help + sb + (to) make informed choices about + N。','Career workshops can help students make informed choices about vocational courses.')],
[('涨价如何推进到健康收益，中间不能省掉什么？','价格提高可能少买，少买可能少摄入，摄入减少才可能降低相关健康风险。'),('已经适量食用的人为什么是反对普遍涨价的理由？','他们承担额外支出，却未必因涨价改变原本适量的摄入，政策负担比目标更宽。'),('糖含量标签与涨价的作用方式有何不同？','标签用风险信息支持选择；涨价用成本激励减少购买并影响所有购买者。')],
'换成提高所有网络游戏价格，写两三句说明适度用户负担及信息工具的替代作用。','Higher prices would increase costs for people who already play games in moderation. Clear reminders of time spent could support informed choices without imposing the same financial burden on every player.')
add('F03','Convenience Food and Traditional Cuisine','同意程度题（完全取代预测）','方便食品可能更普遍，但传统饮食与制作方式因质量体验、文化认同和情感价值而继续存在。',[
('开头：普及与取代不同','承认方便食品便宜省事的吸引力，反对的是由增长推断彻底替代；全篇要证明传统食品仍有位置。',['方便食品日益普遍','出现完全取代预测','承认实用便利','保留传统饮食重要性']),
('让步：疲惫生活推动普及','食品易得、便宜且少准备，符合工作学习后缺乏时间精力的人；这一链支持未来更流行，却尚不能证明彻底替代。',['工作学习后疲惫','不愿花钱费时做饭','方便食品易得省力','未来更普遍']),
('反驳：不可仅用便利衡量','有资源时部分人仍选择传统餐；即使工业产品味道营养提高，文化身份与共同制作享用的情感联系仍有独立价值。',['时间资源允许选择传统餐','传统质量体验仍具吸引力','文化认同超出实用性能','共同准备与享用增强情感纽带']),
('结尾：共存的预测','同时保留方便食品继续普及和传统饮食仍占重要位置，准确反对完全取代，未改成方便食品不能成为主流。',['方便食品有实用收益','传统饮食有体验文化价值','两类饮食可能共存'])],
[('convenience与access各自配介词',1),('共同制作增强而非创造唯一情感',2),('普及不等于完全取代',3)],
[
('the convenience of and ready access to','并列名词各带介词：the convenience of + N；ready access to + N。','Learners value the convenience of and ready access to recorded lectures.'),
('invest a lot of time in preparing','时间投入：invest time in + V-ing；in不是to。','Residents may be unwilling to invest a lot of time in maintaining a shared garden.'),
('pale into insignificance','相对不重要：X pale into insignificance compared with + Y。','Small savings may pale into insignificance compared with the value of reliable medical care.'),
('represent the cultural identity of a group','文化象征：represent the cultural identity of + 群体。','Local festivals can represent the cultural identity of a group.'),
('their emotional bond can be strengthened','关系结果：an emotional bond can be strengthened by + V-ing。','The emotional bond between teammates can be strengthened by working towards a shared goal.')],
[('为何“更普遍”不等于“完全取代”？','更普遍只说明份额或使用增长，仍可能有消费者为其他价值选择传统饮食。'),('即使方便食品味道营养提高，传统饮食还有哪些价值？','传统食品体现文化身份，朋友家人共同准备和享用又可增强情感纽带。'),('convenience与access分别接什么介词？','the convenience of something；ready access to something。')],
'换成电子书与纸质书，用两三句承认便利增长，再说明不能完全取代的体验价值。','The convenience of and ready access to digital books may make them more popular. Yet readers who value the physical experience of reading may continue to buy printed editions, so growing popularity does not imply complete replacement.')
add('A01','Restrictions on Advertising to Children','同意程度题（儿童广告禁令）','承认准确儿童广告的信息和商业价值，重点支持禁止误导食品广告并严格限制诱导不健康饮食的促销。',[
('开头：限定禁令对象','先说明广告销量收益与儿童易受影响，再将支持范围限定为误导性食品广告，避免直接推出所有儿童广告必须禁止。',['儿童市场带动广告','儿童易受营销影响','准确广告有信息价值','限制误导食品广告']),
('让步：商业信息的双向价值','企业触达童书玩具潜在顾客并提高销量；儿童获得价格口味质量信息，在多选项中有机会作知情决定。',['企业介绍新品触达目标群体','消费者注意到产品','儿童获取价格口味质量信息','支持知情选择并提升销量']),
('风险：辨别能力与诱导摄入','夸大视觉让儿童冲动求购，可能经高热量过量摄入增加肥胖风险；赠品又模糊食物需要和玩具诱惑，说明限制的针对性。',['儿童难辨夸大和营销意图','视觉与赠品诱导求购','可能过量摄入高热量食物','支持误导广告禁令与促销限制']),
('结尾：能力差异支持保护','儿童尚不能以成人同等理解力评估广告，部分商家利用这一差异，因此支持禁误导广告；结论与主体段范围一致。',['承认销量与信息收益','儿童理性理解有局限','营销可能利用局限','支持禁止误导广告'])],
[('benefits后关系从句补that',1),('肥胖论证补过量摄入环节',2),('误导广告与促销限制范围',2)],
[
('the benefits that accrue to companies and children','利益归属：benefits that accrue to + 受益者；that引导定语从句。','The benefits that accrue to local residents should be considered when funding festivals.'),
('a wide array of options','选项多样：choose among / offer + a wide array of + 复数名词。','Public libraries offer a wide array of options for independent study.'),
('the fine line between persuasive advertising and misleading information','相近概念边界：the fine line between + A + and + B。','Teachers should recognise the fine line between encouragement and excessive pressure.'),
('are susceptible to such strategies','易受影响：be susceptible to + N；不表示必然上当。','Inexperienced tourists may be susceptible to misleading sales tactics.'),
('make the distinction between','辨别两者：make the distinction between + A + and + B。','Students need to make the distinction between memorising a rule and understanding its use.')],
[('准确儿童广告给企业和儿童各提供什么？','企业触达目标顾客促进销量；儿童获得价格口味质量信息帮助知情选择。'),('广告与儿童肥胖之间应补哪一中间步骤？','夸大和赠品诱导冲动求购，可能鼓励高热量食品过量摄入，再促成肥胖风险。'),('本文支持禁所有儿童广告吗？','没有；重点禁止误导性食品广告，并限制鼓励不健康饮食的促销方式。')],
'换成面向老人的保健产品广告，写两三句区分信息价值与误导保护，不声称医疗效果。','Accurate advertising can help older consumers compare product prices. However, misleading promises may exploit limited knowledge, so regulators should restrict deceptive claims while preserving access to useful information.')
add('A02','Why Advertising Still Works','双边讨论与个人观点','泛滥确实让人忽略广告，但网红信任、品牌熟悉感与算法匹配仍能促成购买。',[
('开头：呈现两种效果判断','一方看广告促进销售，另一方认为无处不在削弱说服力；后文分别解释主动忽略和仍然有效的机制。',['广告行业推动销售','观点分为有效与被忽略','比较两种注意与购买机制']),
('一方：习惯性忽略','多年被商业信息轰炸使人形成忽略习惯；视频插播被跳过或用来办其他事，说明接触次数不等于真正注意。',['商业信息无处不在','形成忽略习惯','跳过插播或分心','内容说服效果减弱']),
('另一方：推荐者信任','网红内容既贴合品牌又激发粉丝兴趣；直播演示通过粉丝对推荐者的信任促成即时购买，用情景而非无来源销量。',['网红制作贴品牌内容','激发粉丝兴趣','演示得到信任','可能立即购买']),
('个人观点：记忆与匹配仍发挥作用','表面不注意时也可能记住品牌，购物时偏好熟悉产品；算法分析浏览购买历史，把相关广告送给已有兴趣的人，降低被忽略概率。',['被动接触留下品牌熟悉感','购物时倾向熟悉品牌','浏览购买历史支持算法匹配','相关性提高广告注意机会']),
('结尾：忽略与有效可并存','对广告司空见惯并不能推出全部失效；社交推荐和技术匹配仍可能刺激消费，重申作者总体判断。',['消费者尝试忽略泛滥广告','社交媒体与技术改变方式','仍可能刺激消费'])],
[('habit of doing与不可数指代',1),('无来源销量改成信任情景',2),('closure改成明确的表面忽略',3)],
[
('the habit of ignoring it','习惯结构：develop the habit of + V-ing；it回指不可数advertising。','Students can develop the habit of checking their work before submission.'),
('aligns with brand images','与目标一致：align with + N；aligns由单数主语决定。','Vocational training should align with local employment needs.'),
('sparks their followers’ interest','激发兴趣：spark + 人’s interest in + N/V-ing。','A visit to a museum can spark pupils’ interest in local history.'),
('be inclined to choose','倾向行为：be inclined to + V；不是必然选择。','Learners may be inclined to choose courses recommended by trusted classmates.'),
('stimulate consumer spending','经济作用：stimulate + spending/demand；需说明信息或激励机制。','Improved access to town centres may stimulate consumer spending in local shops.')],
[('被广告轰炸为什么可能削弱说服力？','人们形成忽略习惯，跳过广告或在插播时分心，接触并未变成内容注意。'),('作者认为广告仍有效的三种机制是什么？','粉丝信任网红推荐、反复接触留下品牌熟悉感、算法提高内容相关性。'),('为什么不能用一个精确直播销量断言广告普遍有效？','材料未提供数字来源，单次销售记录也不能证明所有情景都有相同效果。')],
'换成大学课程宣传，用两三句说明熟悉感和兴趣匹配怎样支持报名。','Students may ignore general course advertisements yet still remember familiar institutions. Messages that align with their interests and include trusted peer recommendations may therefore continue to influence enrolment decisions.')
add('A03','Advertising and Real Consumer Needs','同意程度题（销量来源）','高销量既反映营销力量，也可能回应实际需求；广告与真实需要可以共同作用。',[
('开头：明确高销量的所指','承认广告能引导购买多余商品，但立场讨论的是高销量的来源，不能让this trend误指无用消费再说它体现真需求。',['广告用于推动销量','部分购买可能多余','高销量受营销影响','也反映实际需求']),
('营销作用一：推荐唤起兴趣','网红内容贴合品牌形象，激发即使已拥有相似产品的粉丝兴趣；信任演示可让兴趣转为即时购买。',['贴品牌的网红内容','粉丝兴趣被激发','信任推荐与产品演示','可能立即购买']),
('营销作用二：算法发现受众','浏览与购买历史帮助广告找到潜在需求群体；专门教材之类细分产品因此更容易触达受众，论证的是匹配能力。',['网络购物积累行为信息','算法生成匹配广告','细分产品连接潜在消费者','有助产品推出']),
('反驳排他性：需求仍影响选择','受广告影响不表示不考虑需要；消费者权衡用途与成本会拒绝部分推销品，而补购旧物的广告可回应已经存在的需求。',['消费者权衡需求与成本','拒绝部分产品保留实用品','补购场景已有实际需要','广告可以回应而非创造需求']),
('结尾：共同解释而非二选一','高销量可以体现广告推动过度消费，也部分体现基本和增长的需要；保留can和to some extent以匹配论证。',['营销可能推动过度消费','消费者也有实际需要','高销量由两者共同解释'])],
[('高销量指代避免立场矛盾',0),('受影响不等于买所有商品',3),('定向广告不必然证明需求',3)],
[
('acts as a catalyst for','推动现象：act as a catalyst for + N/V-ing；不是唯一原因。','International cooperation acts as a catalyst for scientific exchange.'),
('run through algorithms','信息处理：data are run through + 算法/系统；run过去分词同形。','Traffic data can be run through algorithms to identify congested routes.'),
('weigh their needs against the cost','比较权衡：weigh + A + against + B。','Policymakers should weigh the benefits of new stadiums against the cost.'),
('serve a practical purpose','有实际用途：serve + a practical purpose；不等于只追求低价。','Community language classes serve a practical purpose for new residents.'),
('respond to an existing need','回应已有需求：respond to + N；区别于制造需要。','Evening childcare can respond to an existing need among shift workers.')],
[('为什么“受影响就会买所有商品”的反证不成立？','影响可以是部分或有限的，受影响的人仍会筛选商品，不能把影响等同于失去所有判断。'),('本文用什么具体情景说明广告回应需求？','消费者需要更换以前买过的物品时，补购广告可回应已经存在的需要。'),('结尾如何避免广告与需求二选一？','同时承认广告推动销量甚至过度消费，以及实际需要对高销量的贡献。')],
'换成大学专业选择，用两三句说明宣传影响与实际职业兴趣可以同时存在。','Course advertising may attract applicants, but students can still weigh their career needs against the cost. A well-designed programme may respond to an existing need rather than merely create demand through promotion.')
add('A04','Economic and Social Effects of Advertising','双边讨论与个人观点','广告推动产品推广与消费，但可能制造物质和身材焦虑；政府监管内容，消费者更批判地判断。',[
('开头：经济与心理两条评价线','一方看繁荣，另一方看物质主义与消费社会；contributing cause保留广告是促成因素之一的范围。',['广告促经济繁荣','广告也可能促成物质主义','分别讨论经济收益与社会心理代价']),
('经济理由：产品信息匹配','广告向潜在买家介绍属性，定向信息激发相关受众兴趣，使专门教材等细分产品更易推出，再落到消费与增长。',['介绍产品属性','定向匹配潜在买家','细分产品更易触达受众','消费与经济增长可能增加']),
('社会代价：理想形象转化压力','广告把幸福与财富联系，使人将物质当快乐标志；不现实身材标准可能导致自我不满和不健康习惯，也推动理想化产品消费。',['广告关联幸福与物质','将理想身材塑为标准','产生自我不满','可能出现不健康习惯或追逐产品']),
('结尾：分工缓解','政府限制广告内容以减少误导，消费者用更批判态度作理性选择；两类措施分别对准信息供给和个人判断。',['承认经济收益与社会代价','政府监管内容','消费者批判判断','支持理性购买'])],
[('小众产品例子精确分类',1),('零脂肪改为不现实纤瘦形象',2),('追求身材与不健康行为因果',2)],
[
('acts as a vehicle for promotion','承担传播功能：act as a vehicle for + N；vehicle为比喻。','A local festival can act as a vehicle for cultural exchange.'),
('prospective buyers','潜在购买者：introduce products to / attract + prospective buyers。','Clear online descriptions can help prospective buyers compare handmade products.'),
('beyond the reach of all but the wealthy','可获得性差距：be beyond the reach of + 人；all but此处为除……之外皆。','High university fees may put some courses beyond the reach of all but the wealthy.'),
('material possessions','物质财产：regard material possessions as + 评价；不是精神财富。','Children should not learn to measure personal worth solely through material possessions.'),
('adopt a more critical attitude','主动判断：adopt a critical attitude towards + N。','Students should adopt a more critical attitude towards unverified online information.')],
[('定向广告为何有经济价值？','它介绍产品属性并匹配潜在买家，帮助包括细分产品在内的商品触达受众，刺激消费。'),('广告如何从理想身材推进到社会心理代价？','不现实形象成为标准，消费者对自己不满，可能发展不健康习惯或为追逐理想而购买。'),('政府与消费者的措施分别管哪一环？','政府监管广告内容；消费者提高判断能力，以更批判态度作理性购买决定。')],
'换成社交媒体健身内容，用两三句承认信息价值并解释理想形象压力，给出判断建议。','Fitness videos can introduce useful activities, but idealised images may make viewers dissatisfied with their appearance. Users should adopt a more critical attitude and choose routines that fit their own needs.')
add('A05','Advertising New Product Features','原因＋积极消极判断双问','企业强调新功能来提高销量；虽能促进真实创新，夸大新颖性诱导重复购买与额外支出使本文总体负面。',[
('开头：两问分别回答','直接交代强调新特征是为了销量，并承认创新收益，同时点出误用营销会制造焦虑，为整体负面评价铺路。',['宣传新品功能','目标是提高销量','可能激励创新','误用引起焦虑与消费主义']),
('原因：新功能怎样促销','新功能吸引潜在顾客并区分竞争产品；手机功能、湿厕纸体验与面膜成分是企业提出卖点的说明情景，不是销量证明。',['突出功能吸引注意','宣称比竞争产品更满足需求','促使获取最新型号或产品','提高商业成功机会']),
('评价：真实改善与夸大诱导比较','真实创新可使消费者受益，但夸大普通产品不足会制造焦虑；缺少实质改善仍反复购买带来不必要负担，是总体负面判断依据。',['真实创新改善产品','夸大差异制造不足感与焦虑','超出真实需要购买','无实质改善的重复消费增加负担']),
('结尾：原因与判断一起回收','再次回答销量动机，并把负面对象精确为夸大新颖性的广告；承认真实创新不消除其引起的不必要需求。',['企业追求商业成功','承认部分创新收益','夸大新颖制造焦虑与需求','总体对社会不利'])],
[('逗号拼接与get hands on',1),('满足需求的搭配与竞争对象',1),('总体负面补具体财务理由',2)],
[
('put a premium on','高度重视：put a premium on + N/V-ing；不是字面溢价。','Employers may put a premium on practical experience when recruiting technicians.'),
('get their hands on','获得想要物品：get one’s hands on + N；hands复数，介词on。','Young readers may queue to get their hands on a popular novel.'),
('distinguish themselves from the competition','与竞争者区分：distinguish A from + B；the competition指竞争对手整体。','Small museums can distinguish themselves from the competition through local expertise.'),
('the resulting benefits could accrue','收益归属：the resulting benefits could accrue to + 人；benefits作主语。','If buses become more reliable, the resulting benefits could accrue to workers and students.'),
('places an unnecessary financial burden on consumers','财务代价：place a financial burden on + 承受者。','Frequent changes to school uniforms place an unnecessary financial burden on parents.')],
[('题目要求回答哪两问？','为什么企业强调产品新特征，以及这种发展总体积极还是消极。'),('作者承认的正面价值是什么？','强调新功能可能推动真实创新，让消费者享受实质产品改善。'),('总体负面判断的具体权衡依据是什么？','夸大新功能引起焦虑，使人在没有实质改善时反复购买，承担超出真实需求的不必要支出。')],
'换成教育软件不断强调新功能，写两三句比较真实学习改善与升级焦虑带来的开销。','New features can improve educational software when they solve genuine learning problems. However, advertising minor updates as essential may encourage repeated purchases without better results, placing an unnecessary financial burden on families.')
add('L01','The Rise of Dominant Languages','积极或消极发展判断','总体积极：跨国经济与科学沟通收益较大；少数语言文化损失仍需重视，新文化不能完全替代旧传统。',[
('开头：趋势与总体判断','主流语言受重视与少数语言使用减少同时发生；以经济和科学交流收益支持积极判断，并承认传承压力。',['全球化提升通用语需求','少数语言使用减少','文化传承承压','经济与科学收益支持积极评价']),
('经济收益：合同与商业关系','国际贸易提供市场机会，掌握主流语言帮助谈合同更顺畅；外国商人学习中文是沟通促进商业联系的说明例。',['跨国贸易创造市场机会','使用共同语言降低沟通障碍','合同协商更顺畅','商业关系与经济福祉改善']),
('科学收益：共享成果','论文与国际研讨需要共同沟通媒介；英语可减少语言壁垒，让知识覆盖更广并支持不同国家研究者合作。',['研究成果需要跨国传播','共享语言减少语言障碍','更多人获取知识','国际科研合作更容易']),
('文化代价：损失仍真实存在','母语使用减少可能削弱独特世界观与文化身份；主流语本地化会创造新文化形式，但这种融合只能补充，不能证明旧损失不重要。',['少数人使用母语','独特文化观念与实践传承减弱','主流语吸收地方元素','出现新形式但原损失仍在']),
('结尾：比较收益与不可替代代价','生活机会和跨境知识获取是权衡依据；明确新文化不能完全替代流失传统，避免用趋势难逆转代替正负判断。',['语言主流化继续','经济生计与知识传播收益','文化传统可能流失且不可完全替代','总体积极但重视成本'])],
[('贡献经济用contribute to',1),('新文化不抵消原文化损失',3),('正负判断需要收益比较',4)],
[
('place a premium on','高度重视：place a premium on + N/V-ing。','Universities should place a premium on helping students evaluate evidence.'),
('foster and cement business relationships','建立并巩固关系：foster/cement + relationships with + 人。','Joint community projects can foster and cement relationships between neighbours.'),
('break down language barriers','减少沟通障碍：break down + barriers to + N/V-ing。','Accessible teaching materials can break down barriers to adult education.'),
('a lingua franca','共同交流语言：use/need + a lingua franca；单数可数名词需冠词。','An international sporting event may need a lingua franca for volunteers from different countries.'),
('widen access to knowledge','扩大获取机会：widen access to + N；access通常不可数。','Free public libraries can widen access to knowledge in disadvantaged communities.')],
[('通用语给经济和科学各带来什么机制性收益？','经济上帮助合同协商和关系建立；科学上减少语言壁垒，扩大知识共享并促进合作。'),('新文化出现为什么不能证明少数文化损失无关紧要？','新文化形式不能完全替代少数语言承载的独特传统、世界观与身份。'),('结尾如何真正回答positive or negative？','以生计改善和跨国知识获取比较文化成本，给出总体积极判断，同时保留对损失的重视。')],
'换成全球统一技术标准，写两三句说明协作收益及本地方法可能损失，给有边界的总体评价。','Shared technical standards can reduce barriers to cooperation and widen access to knowledge. On balance, these benefits may be substantial, although local methods that serve distinctive needs should also be preserved.')
add('L02','Machine Translation and Language Learning','同意程度题（是否仍需学习）','不同意机器翻译让外语学习不再必要；正式沟通的细微意义与文化职业收益仍支持学习。',[
('开头：工具成功不等于取消学习','准确呈现不再需要学习的主张，而非不应该学习；作者承认工具普及却否定其消除所有学习必要性。',['机器翻译进步','提出无需外语学习','工具广泛使用','仍有学习必要']),
('反方：工具便利与时间成本','应用识别并翻译文本语音，让日常交流和阅读更容易；支持者据此比较多年学习与其他科目投入，但使用工具不自动证明学习浪费。',['翻译工具处理日常内容','减少沟通与阅读障碍','学习外语需要多年投入','反方主张时间投向其他学科']),
('反驳一：正式交流的语义要求','医疗或商务讨论不仅传词，还涉及语气、态度、细微含义、术语与情感；语言能力或熟练口译帮助防止信息失真。',['正式交流需要细节准确','理解语气情感与专业术语','人工语言能力补足理解','降低信息混乱和遗漏风险']),
('反驳二：文化与职业范围','学习语言打开相关文化入口，并在全球化企业中扩大职业选择；例子用于说明文化接触与机会，不应当作保证就业的事实。',['学习语言获得文化入口','理解饮食服饰等传统','沟通能力适用于跨国企业','未来职业选择可能增加']),
('结尾：工具与学习并存','承认机器翻译帮助沟通，同时总结正式场合的顺畅沟通与额外文化职业价值，因此应继续学习。',['机器翻译便利沟通','正式语义仍需语言能力','文化与职业收益额外存在','支持继续外语学习'])],
[('宾语从句语序与必要性范围',0),('机会成本属于反方观点',1),('prevent消息结构与并列',2)],
[
('spare students the trouble of learning','省去麻烦：spare + sb + the trouble of + V-ing。','Clear transport information can spare visitors the trouble of asking for directions.'),
('develop a good command of','形成熟练掌握：develop a good command of + 语言/知识领域。','Apprentices need to develop a good command of basic safety procedures.'),
('would otherwise be spent on','机会成本：time that would otherwise be spent on + N/V-ing。','Time that would otherwise be spent on paperwork could be used for lesson planning.'),
('prevent the message from getting garbled','防止失真：prevent + N + from + V-ing；message为被影响对象。','Careful instructions can prevent new employees from making avoidable mistakes.'),
('have access to a specific culture','获得文化入口：have access to + N，不把access当可数。','Affordable exhibitions give schoolchildren access to a wider range of artistic traditions.')],
[('机器翻译方便为什么还不足以否定语言学习？','日常功能不能覆盖正式场合的语气细节与术语，学习还带来文化和职业价值。'),('学习者仍使用翻译工具能证明学习时间浪费吗？','不能；工具可补足专业文本或效率需求，使用工具与学习有价值可以同时成立。'),('prevent的句法槽位是什么？','prevent + 人/事物 + from + V-ing，例如prevent the message from getting garbled。')],
'换成AI写作工具，写两三句承认便利并说明学生仍需学习写作的理解判断价值。','Writing tools can spare students the trouble of drafting routine phrases. However, students still need to understand arguments and evaluate evidence, since a fluent output does not guarantee that its reasoning is sound.')
add('L03','Supporting Struggling Language Learners','同意程度题（是否免除强制学习）','不赞成因缺乏天赋就放弃；保留所有学生基础外语要求，以合理目标和额外支持控制困难学生时间成本。',[
('开头：要求与支持一起提出','承认部分学生学习困难，但把受益判断附上教学适配条件；后文必须解释如何兼顾努力与负担。',['部分学生外语天赋较弱','出现允许停止学习主张','外语学习仍有收益','教学需适应学习需要']),
('反方：挫折与机会成本','母语和英语差异较大可能使学习困难、挫伤自信；停止学习释放时间给其他学科，翻译工具又为日常沟通提供替代。',['语言差异增加学习困难','受挫与自信下降','停学可把时间投向其他学科','翻译工具降低部分沟通需求']),
('反驳：未精通仍有价值','基础程度也能打开文化入口、拓宽视野，继续学习还可能增加职业选择；未达到精通并不能证明过程收益为零。',['未必能精通外语','基础学习仍接触语言与文化','视野得到拓宽','持续学习可能扩大未来职业机会']),
('回应强制问题：时间与教学适配','短期结果不应决定全部学习价值，能力可经练习发展；合理目标与额外支持让学校保留基础要求，又不要求困难者过度投入。',['进步需要持续练习','不只看即时表现','设置可达到目标与额外支持','保留基础学习并控制额外时间成本']),
('结尾：有限要求而非统一高标准','总结文化和沟通收益，保留普遍基础学习要求，但明确教学与预期应因人调整，使强制立场有实施边界。',['困难不消除文化沟通收益','所有人保留基础要求','教学与预期适应学生需要'])],
[('困难不能改写成完全无能力',1),('短期结果不能决定全部价值',3),('普遍要求必须有适配支持',4)],
[
('a natural aptitude for','天赋能力：have/lack a natural aptitude for + N/V-ing。','A natural aptitude for drawing does not remove the need for regular practice.'),
('have little in common with','相似度低：A have little in common with + B。','A classroom simulation may have little in common with the pressure of a real workplace.'),
('devote themselves to other subjects','投入领域：devote oneself/time to + N/V-ing，to为介词。','Employees could devote more time to developing transferable skills.'),
('a means of broadening their horizons','途径作用：a means of + V-ing；broaden one’s horizons拓宽视野。','Volunteering can be a means of broadening young people’s horizons.'),
('with teaching and expectations adapted to their needs','条件配套：with + N + 过去分词；adapt X to + 需要。','A public exercise programme can be inclusive, with activities adapted to participants’ needs.')],
[('未精通语言为什么不等于学习无价值？','基础学习仍能接触文化、拓宽视野，继续学习也可能增加沟通和职业机会。'),('作者如何回应困难学生的时间成本？','设定可达成目标并给予额外支持，保留基础学习，不要求他们过量投入。'),('本文是要求所有人达到同等高水平吗？','不是；要求保留基础学习，但教学和预期随学生需要调整。')],
'换成学生体育课，用两三句说明能力较弱者仍能受益，以及怎样保留要求并调整教学。','Pupils who lack a natural aptitude for sport can still benefit from basic physical education. Schools should retain participation requirements, with activities adapted to individual abilities and achievable goals.')
add('C01','Parenting and Juvenile Crime','同意程度题（评估only）','良好家庭教育重要但并非唯一办法；还需限制有害媒介接触，并按罪行、成熟度和责任适当量刑。',[
('开头：重要不等于唯一','题眼solely要求判断是否唯一解决办法；承认父母指导核心作用，再提出其他因素与措施，避免反驳成父母不重要。',['少年犯罪有社会成本','主张只改善家教','承认家教重要','其他因素仍需其他措施']),
('家教作用：道德理解与行为示范','好的榜样帮助孩子认识道德和犯罪后果；相反，家暴可能使孩子把暴力当正常解决冲突方式，继而对外模仿。',['父母提供榜样与道德引导','孩子理解行为对自己和受害者的影响','减少街头违法风险','暴力榜样可能诱发相反学习']),
('非唯一：媒介影响未被覆盖','有害内容可能为儿童提供模仿模式，特别在类似情境；这支持限制儿童接触内容，说明家教不能包办全部外部影响。',['接触暴力等有害媒介内容','在相似情境中可能模仿','家庭引导未覆盖全部影响','需要更严格内容接触监管']),
('补充威慑：个体责任评估','仅因年龄预期过轻处罚可能削弱威慑；量刑应评成熟度与责任，严重蓄意犯罪可受重罚，但必须相称且有依据。',['预期过轻处罚削弱部分威慑','评估成熟度与可责性','考虑蓄意程度及罪行严重性','适用相称刑罚']),
('结尾：三类工具分工','家教、内容限制、相称处罚分别作用于成长榜样、外部接触与犯罪后果；总结多因素所以不应只用家教。',['家庭榜样减少风险','媒介限制减少有害接触','相称处罚兼顾成熟度','多工具回应多因素'])],
[('限定性关系从句去逗号',1),('媒介内容分类与可能性',2),('成熟度评估不冒充法律事实',3)],
[
('set a good example for','行为示范：set a good example for + 人；example可被关系从句展开。','Teachers can set a good example for pupils by checking uncertain information.'),
('have a propensity for aggressive behaviour','描述倾向：have a propensity for + N/V-ing；不代表必然行为。','Some businesses have a propensity for prioritising short-term sales over service quality.'),
('be it in video games or violent movies','两类场景推广：be it + A + or + B，正式表达。','Students need reliable guidance, be it in academic study or vocational training.'),
('the extent to which they are culpable','程度限定：the extent to which + 主谓；culpable为应负责任。','Schools should consider the extent to which their rules affect disadvantaged families.'),
("take the offender's maturity into account",'纳入判断：take + 因素 + into account。','Course designers should take learners’ prior knowledge into account.')],
[('如何准确反驳only而不否定父母作用？','先解释家教如何减少犯罪，再说明媒介影响和威慑不足也需要针对性措施。'),('暴力父母的榜样机制是什么？','孩子反复看到暴力，可能将其接受为解决冲突方式，并模仿到家庭外。'),('支持较重处罚前要评哪些条件？','罪行严重性、蓄意程度、个人成熟度与责任程度，刑罚须与这些条件相称。')],
'换成“减少肥胖唯一办法是家长教育”，写两三句承认家教价值并补学校或环境措施。','Parents can set a good example for children by preparing balanced meals. However, reducing childhood inactivity also requires safe play spaces and opportunities for exercise at school, so parenting is only one part of the response.')
add('C02','Sentencing Young and Adult Offenders','同意程度题（严重少年犯罪同罚）','刑罚须与罪行相称，但不应仅按年龄机械同罚；应评估判断能力、成熟度和责任，严重蓄意犯罪仍可重罚。',[
('开头：相称与灵活并存','不纵容严重犯罪，但区分犯罪危害与少年个体情形；支持相关情况下灵活量刑，而非一律成人处罚。',['过轻处罚可能削弱威慑','讨论成人刑罚是否同样适用','坚持罪刑相称','允许少年情形下灵活量刑']),
('支持同罚：理性成本计算','对会权衡得失的人，预期处罚超过犯罪收益可能有威慑；同罚支持者据此排除年龄减刑，但这依赖理性选择前提。',['潜在犯罪者比较收益与风险','处罚成本高于预期收益','可能不实施犯罪','支持者主张只按罪行处罚']),
('反驳：外部影响与判断条件','不良引导、家庭暴力等可能塑造少年行为；只有这些因素实际削弱判断时，才构成审慎减罚理由，存在背景因素不自动免责。',['外部环境持续影响少年','可能把暴力接受为正常','判断能力受到影响','据此考虑适度减轻处罚']),
('边界：评估而非自动宽免','不能让年龄带来必然轻罚预期；逐人评估成熟度、责任和危害，严重蓄意且责任较高时可以适当长期监禁。',['年龄宽免预期可能削弱威慑','逐人评估成熟度与责任','结合蓄意程度和实际危害','适用适当严厉处罚']),
('结尾：年龄只是一个指标','按法律量刑仍允许考虑年龄及成熟度差异；兼顾个体情形和威慑目标，保留全篇有限灵活立场。',['依法且罪刑相称','年龄作为成熟度指标之一','允许相关情形的灵活性','保留威慑目标'])],
[('proportionate与威慑限定',1),('外部因素到判断受损的条件',2),('个别评估替代未核实法律概括',3)],
[
('proportionate punishment','相称处罚：punishment proportionate to + 罪行；形容词用proportionate。','Schools should use proportionate sanctions for repeated rule violations.'),
('weigh the benefits against the risks','权衡两侧：weigh + benefits + against + risks。','Tourists should weigh the benefits of remote travel against the risks to fragile environments.'),
('be a mitigating factor','减轻情形：X may be a mitigating factor；不是自动免罚条件。','A lack of clear instructions may be a mitigating factor when assessing an employee’s mistake.'),
('are led astray by extrinsic factors','受到外在因素误导：be led astray by + 原因；lead过去分词led。','Young consumers may be led astray by exaggerated claims about expensive products.'),
('tailored to the maturity of delinquents','按特征适配：tailor + N + to + 需要/特征；被动为be tailored to。','Support sessions should be tailored to the needs of new language learners.')],
[('支持同罚的威慑论依赖什么前提？','潜在犯罪者会理性比较预期收益与处罚风险，并因此调整行为。'),('有不良家庭环境就应自动减刑吗？','不应；要看这些影响是否实际损害该少年的判断能力，并作审慎评估。'),('作者怎样避免年龄变成一律宽免？','逐人评成熟度和责任，同时考虑蓄意程度与危害，严重犯罪仍允许相称重罚。')],
'换成学校违纪处分，写两三句兼顾相称后果与个体判断能力，不自动免罚。','School sanctions should be proportionate to the harm caused. However, teachers should assess whether unclear guidance affected a pupil’s judgment, rather than treating age alone as a reason for either identical or lighter penalties.')
add('C03','Longer Sentences and Crime Prevention','双边讨论与个人观点（长期策略比较）','更长刑期能威慑部分人，但教育、家长榜样与有害媒介限制可在犯罪前处理动机和影响，长期更有效。',[
('开头：两条减罪路线','题目要求讨论更长刑期与其他办法，先中立列出两路线，随后解释威慑的条件和预防的比较优势。',['社会需要减少犯罪','一方主张延长刑期','另一方支持替代办法','比较威慑与预防机制']),
('支持长刑期：改变预期得失','部分人在犯罪前算成本收益，更长刑期提高损失，使其不再值得；可能放弃抢劫是说明情景，不是所有犯罪者都会算账。',['犯罪前权衡奖励与处罚','长刑期提高预期代价','代价可能超过收益','部分潜在犯罪者停止行动']),
('局限与教育：处理动机','一些人冲动或相信能逃脱处罚，刑期增加难改变其选择；道德判断与非暴力解冲突教育直接作用于动机。',['部分犯罪者不评后果或自信逃脱','延长刑期作用有限','教育认识伤害并练非暴力处理','改变长刑期未触及的动机']),
('外部预防：家长与内容监管','家庭暴力可能示范冲突处理方式，媒体有害内容可能被模仿；家长好榜样和政府接触限制分别减少这两类外部影响。',['家庭与媒介提供行为模式','部分孩子模仿暴力','父母示范良好方式','政府限制有害内容接触']),
('结尾：以犯罪前干预比较','承认更长刑期对部分人有威慑，但替代方法在犯罪发生前处理内在动机和外部影响，因此提出长期更有效的比较判断。',['长刑期威慑部分人','单靠刑期无法涵盖全部原因','教育榜样监管前置干预','长期方案更全面'])],
[('威慑只适用于部分理性决策者',1),('教育须说明改变什么动机',2),('用犯罪前预防解释长期比较',4)],
[
('weigh the potential rewards against the punishment','得失比较：weigh + 收益 + against + 代价。','Employees may weigh the potential rewards of promotion against the additional workload.'),
('refrain from offending','克制行动：refrain from + V-ing，from后不可接原形。','Consumers may refrain from buying unnecessary products when they track their spending.'),
('escape justice','逃脱应负后果：escape + justice，不加from。','Stronger checks can make it harder for fraudulent advertisers to escape justice.'),
('developing moral judgment','培养判断：develop + 能力名词；developing为by后的V-ing。','Literature discussions can help pupils develop moral judgment without prescribing a single answer.'),
('make concerted efforts','共同协作：make concerted efforts to + V；说明参与主体。','Schools and families should make concerted efforts to support struggling readers.')],
[('更长刑期为什么不能对所有人同样有效？','部分人不考虑后果，或觉得能逃脱处罚，延长刑期没有改变其决策前提。'),('教育在本篇中不是空泛口号，它具体改变什么？','帮助理解对受害者与自己的伤害，形成道德判断，并学习非暴力解决冲突。'),('替代方案的长期比较依据是什么？','它们在犯罪发生前处理动机和家庭媒介影响，覆盖长刑期未改变的原因。')],
'换成校园欺凌，用两三句说明处罚之外为何需要冲突处理教育与成人榜样。','Strict penalties may deter some bullying, but they may have limited effects on pupils who act impulsively. Schools and families should make concerted efforts to teach non-violent conflict resolution and model respectful behaviour before harm occurs.')
add('C04','Reducing Reoffending after Release','原因与措施双问','难找工作与社会排斥可能促成再犯；监狱及释放后的教育就业项目提升能力、稳定生活并帮助重建关系。',[
('开头：两个原因与对应项目','再犯不是不知道后果就能解释；开头列出就业与社会支持缺口，再提出教育就业项目，后文需分别连接原因。',['释放后仍有再犯','找不到工作','缺乏社会支持','教育就业项目回应']),
('原因一：经历断层与生计','长期监禁若缺训练，会失去近期工作经验和雇主所需技能；假设年轻人服刑十年后更难竞争，生计压力增加再犯风险。',['长期服刑缺近期经验和训练','不满足雇主需求','求职竞争受阻','生计困难增加再犯风险']),
('原因二：标签造成排斥','邻里刻板看法与不信任减少重建生活机会，社会关系难恢复；以may限定排斥与再犯的可能联系。',['服刑结束回到社区','他人标签化并不信任','重建关系与生活机会减少','再犯风险可能上升']),
('措施：技能、日程与关系三环','基础教育与在监工作训练提高就业能力；稳定工作提供收入和日常安排，又通过交往逐步改变负面看法，从而同时回应两个原因。',['教育与工作训练补能力经验','求职机会提高','稳定收入与日程减少失序','工作交往改善他人认知','帮助复归社会']),
('结尾：回收能力到复归','教育就业项目不是只给文凭，而是提高雇用可能性；再由工作与支持对接复归，保持因果措施一致。',['就业和支持不足可能再犯','实施教育与就业项目','提高可雇用性','促进社会复归'])],
[('employers与假设经历明确',1),('处理原因的逻辑主语',3),('就业可能逐步改善偏见',3)],
[
('secure a job','获得稳定岗位：secure + a job/employment；不指工作安全。','Vocational courses can help school leavers secure a job in skilled trades.'),
('a means of livelihood','谋生方式：as a means of livelihood；means单复数同形。','Traditional crafts remain a means of livelihood for some rural households.'),
('a major barrier to employment','就业障碍：a barrier to + N/V-ing；to是介词。','Unaffordable transport can be a major barrier to employment in remote areas.'),
('a sense of self-efficacy and accomplishment','能力信念与成就感：develop a sense of + 抽象名词。','Completing a group project can give students a sense of self-efficacy and accomplishment.'),
('a stabilizing routine','稳定生活安排：provide a stabilizing routine for + 人。','Regular sports sessions can provide a stabilizing routine for new university students.')],
[('长期监禁怎样通过就业影响再犯？','缺少近期经验与训练使求职困难，生计压力又可能增加以非法活动谋生的风险。'),('社会不信任中间损害了什么？','它减少重建生活、关系和机会的可能，排斥才进一步与再犯风险相连。'),('工作项目如何同时回应技能不足与排斥？','它提供技能经验、收入和稳定安排，工作中的关系建立又可能逐渐削弱刻板印象。')],
'换成长期失业者重返职场，用两三句说明培训与真实工作经验怎样共同重建能力和关系。','Training can remove a major barrier to employment by updating skills that have become outdated. Supported work placements can then provide experience, a stabilizing routine and opportunities to rebuild professional relationships.')
add('E01','University and a Successful Life','双边讨论与个人观点（最佳人生路径）','大学对专业和经济机会有价值，但职业培训更适合部分人；成功也涵盖健康与关系，大学不是人人最佳路径。',[
('开头：限定成功含义','先从职业与财务成功切入双方路线，给大学和其他办法公平比较；最后一段再解释为何成功定义需要更完整。',['人们追求职业与经济成功','一方认为大学最有效','另一方认可替代路线','需要结合目标比较']),
('大学理由：资格与岗位需求','学历显示专业知识训练，并是某些职业进入要求；知识密集社会重视受教育劳动者，职业机会与收入有助经济保障，但不是成功保证。',['学历证明专业知识训练','部分职业需要相关资格','更多职业与收入机会','财务保障可能改善']),
('反方：岗位匹配比文凭本身重要','毕业生也可能被拒或从事非本专业；职业培训以具体实操培养水管工厨师等技术能力，更贴合有实践优势的学生。',['大学文凭不保证专业成功','部分岗位更重实作技能','职业培训提供岗位指导','适合技能职业与实践兴趣者']),
('观点兼收尾：路径因人而异','大学与职业培训各服务不同目标；进一步扩展成功到健康和人际关系，从定义层面说明不能把大学当普遍最佳途径。',['大学扩大学术职业机会','职业培训服务技能工种','成功还包括健康与关系','适合个人且均衡发展更重要'])],
[('职业资格例子分类一致',1),('财务优势不等于人生全面成功',1),('职业培训与特定岗位匹配',2)],
[
('a wealth of job opportunities','机会丰富：a wealth of + N；wealth为丰富量而非仅金钱。','Learning digital skills may open up a wealth of job opportunities for older workers.'),
('does not necessarily amount to success','否定等同：X does not necessarily amount to + N。','A large tourism industry does not necessarily amount to prosperity for local residents.'),
('hands-on, job-specific instruction','实践与岗位针对性：provide/receive + hands-on, job-specific instruction。','New museum guides could receive hands-on, job-specific instruction before leading tours.'),
('affords graduates access to','提供机会：afford + 人 + access to + N；不同于afford to do负担得起。','An affordable bus network affords rural residents access to medical services.'),
('should not be defined in terms of','界定标准：define X in terms of + N；被动be defined。','A successful city should not be defined in terms of economic output alone.')],
[('大学怎样改善职业机会？','资格显示专业知识与训练，有些职业需相关资格；知识密集岗位也重视受教育劳动者。'),('职业培训为何可能优于大学路线？','它提供岗位特定的实操技能，更适合目标为技能工种、兴趣优势在实践的人。'),('最后一段怎样从成功定义回应best？','成功还包括健康和强关系，单靠学历与收入不能覆盖，因此大学不是每个人的最佳途径。')],
'换成城市成功标准，写两三句承认经济增长，再扩展到健康与社区关系。','Economic growth can afford residents access to better services, but a successful city should not be defined in terms of income alone. Public health and strong community relationships should also guide investment decisions.')
add('E02','Choosing Academic or Vocational Courses','同意程度题（课程选择与年龄阶段）','支持高中阶段选择学术或职业路线；初中应先完成广泛通识，为个人发展与专业工作打基础。',[
('开头：阶段式立场','既回应技术工人需求，又把自由选择限定在高中；初中保留通识必修，后文需要解释为何专业化不能太早。',['现代经济需要知识与技能','蓝领需求支持职业培训','高中可选择专业路径','初中先完成通识基础']),
('支持职训：需求与课程对接','白领偏好可能造成手工职业缺口，TVET结合技能理论、真实情景与实操准备就业；具体课程如何改善前景是论证重点。',['手工职业存在需求','职业学校提供技能与理论','真实实例和操作经验','毕业后求职前景改善']),
('阶段限制：通识提升专业表现','教育还培养公民责任和智力，不只让人会某份工作；更广基础使技术工人理解、判断和完成任务更好，初等教育不足以替代完整初中基础。',['教育需培养公民与思维能力','通识基础提升专业工作质量','小学基础尚不充分','完成初中后再全时专业化']),
('结尾：明确先后顺序','通识与职业培训不是互斥，答案给出顺序：初中广泛学习，高中按需要选择学术或技术资格。',['初中通识必修','高中自由选择路线','学术或技术资格进入未来路径'])],
[('木工职业与人名类别一致',0),('专业化开始阶段明确',2),('as well as并列完整',2)],
[
('equip students with the skills and knowledge','赋予能力：equip + sb + with + N；不能equip sb of。','Community classes can equip older residents with the skills and knowledge needed for online services.'),
('the alignment between the goal of education and the growing needs of the job market','目标匹配：the alignment between + A + and + B。','The alignment between bus routes and residents’ travel needs can improve public transport use.'),
('hands-on experience','实际操作经验：gain/provide + hands-on experience in + N/V-ing。','Conservation projects give volunteers hands-on experience in maintaining habitats.'),
('a broad foundation in general education','基础构建：a broad foundation in + 领域。','A broad foundation in science can help citizens evaluate environmental claims.'),
('exercise their freedom to choose','行使选择自由：exercise one’s freedom to + V。','Adults should be able to exercise their freedom to choose suitable training courses.')],
[('作者支持哪个阶段开始全时职业专业化？','高中阶段；初中阶段应先完成广泛的通识教育。'),('通识教育为什么不只是与技术培训争时间？','它培养公民意识和智力，并使技术工人凭更广理解把专业任务做得更好。'),('TVET用哪些具体内容准备就业？','行业技能与理论、真实实例以及实操经验，共同提高毕业后的就业前景。')],
'换成青少年体育专业化，写两三句提出先广泛基础再选择专项的顺序并解释作用。','Young athletes need a broad foundation in physical skills before specialising in one sport. Older pupils could then choose more intensive training, while retaining the wider abilities needed for long-term development.')
add('E03','Flexible Ability Grouping','双边讨论与个人观点','支持有条件的灵活分组：按当前学习需求加快或补强教学，保障资源平等并允许组间流动。',[
('开头：两种组织方式','对比混合能力同班与学业能力较强者单独教学；争论焦点是教学组织与特殊支持，不是天赋高低的人格价值。',['学生当前学业能力有差异','一方支持混合教学','另一方支持分别教学','比较公平与学习匹配']),
('混班理由：平等与避免标签','学校像微型社会，接受能力差异并提供共同机会；低成绩者不被单独标记，可能减少自卑和污名对信心的长期伤害。',['共同接受教育机会','不按成绩分离同伴','减少低成绩标签','保护信心与自尊']),
('分组理由：不同速度的适配','混班教师需同时应对广泛需求；分组使学得快者继续推进、需要帮助者获得更合适解释，关键是双方都得到匹配。',['同班学习需要跨度大','按当前表现分组','快者加速且困难者获得支持','更可能发挥潜能']),
('个人观点：公平条件与可变分组','加速教学需同时保障平等资源、允许流动，防止固定标签；学生其他背景仍多样，分组不等于消灭所有多样性。',['按当前学习需求调整教学','保证资源平等','允许组间流动','减少歧视风险并保留其他多样性']),
('结尾：灵活性支持效率','支持的是灵活而非僵化分流；有效资源配置服务于更个性化教学，回扣前段公平条件。',['采用灵活分组','有效配置教学资源','提供较个性化教学'])],
[('As从句需要主句承接',1),('教师复数与差异化需求',2),('分流需有公平资源与流动条件',3)],
[
('mixed-ability classes','混合能力教学：teach students in + mixed-ability classes。','Mixed-ability classes in community sports can encourage mutual support.'),
('feel stigmatized','受污名感：feel/be stigmatized by/as + N；此处可能损害心理。','Residents may feel stigmatized when public support is described as a personal failure.'),
('undermine their confidence and self-esteem','负面心理结果：undermine + confidence/self-esteem。','Repeated public criticism can undermine employees’ confidence and self-esteem.'),
('assimilate new knowledge','理解吸收：assimilate + knowledge/information；不是只死记。','Practical demonstrations can help apprentices assimilate new knowledge.'),
('allowing movement between groups','制度可变性：allow movement between + 复数群组；allowing作伴随补充。','Adult courses can remain flexible by allowing movement between groups as learners progress.')],
[('混班为何可能保护低成绩学生的信心？','他们不按成绩被分离或贴固定标签，减少自卑与污名感。'),('分组怎样让两类学生都受益？','学得快的人按较快速度推进，需要支持的人获得更合适解释和巩固。'),('作者支持分组的三项公平条件是什么？','根据当前需要调整、保证资源获取平等、允许组间流动，避免固定等级与歧视。')],
'换成成人语言班，写两三句说明分级速度收益与动态调整条件。','Grouping adults by current language ability can help teachers provide suitable practice. The system should remain flexible, allowing movement between groups and ensuring that every learner has equal access to resources.')
add('E04','Theory and Practical Training','同意程度题（排除理论）','不同意只保留实操；实操帮助入职，理论帮助理解、分析和应对新问题，大学应兼顾两者。',[
('开头：题眼是排除理论','先承认实操值得重视，再否定因此取消理论的推理；不把题目弱化成实操是否重要。',['大学课程面临取舍','有人主张实操排除理论','实操有价值','排除理论缺乏理由']),
('实操收益：缩短工作适应','毕业生缺真实解决问题经验，企业需另投入培训；强化实操培养专业胜任力、加快工作适应，才可能降低成本增加利润。',['毕业生缺少真实操作经验','企业额外投入培训','实操提升专业胜任力','入职适应更快并可能增利润']),
('理论收益：从例行任务到新问题','机械、会计和教育心理例子都体现同一机制：理解原则让人不只完成常规操作，还能分析突发或复杂情境。',['掌握领域理论原则','理解与批判性分析','系统执行并处理新情境','理论构成专业表现基础']),
('结尾：互补而非替代','把理论知识与实践技能并列为未来成功的重要准备，明确两者应在大学课程中结合。',['实操支持应用','理论支持理解与适应','大学同时训练两者'])],
[('hands-on经验插入语标点',1),('增加实操不等于认可排除理论',1),('理论是重要基础而非全职业必要前提',2)],
[
('little, if any, hands-on experience','程度限定：little, if any, + 不可数名词；if any两侧逗号。','New volunteers may have little, if any, hands-on experience in habitat restoration.'),
('channelled into employee training','资金投入：channel money/time into + N/V-ing；此处被动。','Funds could be channelled into improving public transport reliability.'),
('acquire professional competence','获得专业胜任能力：acquire + competence in + 领域；不是竞争力competitiveness。','Supervised practice helps trainee nurses acquire professional competence.'),
('cope with unforeseeable emergencies','应对突发紧急情况：cope with + N；unforeseeable不能预见的。','Well-trained tour guides may be better able to cope with unforeseeable emergencies.'),
('an indispensable aspect of higher education','必要组成：an indispensable aspect of + N；本篇对象为高教内容。','Critical reading is an indispensable aspect of responsible media use.')],
[('实操为何可能减少企业培训成本？','毕业生已有真实任务经验与胜任能力，入职适应更快，企业少投入补训。'),('三类专业例子共用哪条理论价值链？','理论帮助理解原则、批判分析，再系统处理常规之外的复杂或突发问题。'),('为什么承认实操重要还不足以支持题目？','题目还主张排除理论；理论的独立基础价值使两者需要结合。')],
'换成驾驶训练，写两三句说明操作练习与道路原理知识怎样互补。','Hands-on driving practice helps learners operate a car confidently. Knowledge of road rules and safety principles also helps them interpret unfamiliar situations, so instruction should combine practical skills with clear theoretical guidance.')
add('E05','Study and Extracurricular Activities','同意程度题（兼顾学业与其他活动）','同意：知识学习是基础，课外活动培养社会与组织等能力；两者整合才实现均衡大学教育。',[
('开头：并列必要目标','承认知识获取是基本任务，同时明确课外活动也必要；不是减少学业价值，而是判断大学教育应涵盖什么。',['大学应获取知识','日程应否包含其他活动','学业重要','课外活动同样支持均衡教育']),
('学习理由：专业知识与职业机会','职业分化使劳动力市场更需要知识，勤学改善学业和专业准备；就业、薪资与晋升再连接较高生活水平。',['职业分工知识要求上升','勤学改善知识与学业','专业机会与职业发展扩大','生活水平可能提高']),
('活动理由：交往中的技能习得','社团让志趣相投者交流合作，形成沟通、人际、组织与实践能力；这些能力来自活动过程，不能只靠理论学习获得。',['社团连接共同兴趣者','交流分享与组织活动','练人际沟通组织实践技能','支持未来社会与职业参与']),
('结尾：结合才覆盖两目标','Only when引出倒装，强调知识学习与活动中的社会学习整合，大学才能同时完成学术和社会化目标。',['学业提供知识基础','课外活动促进社会化','整合两类学习','实现双重教育目标'])],
[('activities复数与均衡教育',0),('社团参与才是活动',2),('only when倒装与双重目标',3)],
[
('devote substantial time to their studies','时间分配：devote + time + to + N/V-ing；to是介词。','Local councils should devote substantial time to consulting residents before changing bus routes.'),
('like-minded people','共同兴趣者：interact with / meet + like-minded people。','Community gardens allow residents to meet like-minded people.'),
('sharpen or acquire skills','磨炼或获取能力：sharpen/acquire + skills；不可sharpen人。','Volunteering can help young adults sharpen or acquire skills in teamwork.'),
('an important ingredient of personal socialization','组成因素：an important ingredient of + 过程/结果。','Trust is an important ingredient of effective international cooperation.'),
('Only when the pursuit of academic achievement is integrated with social learning through activities can','必要条件倒装：Only when + 正常从句 + can + 主语 + V。','Only when safer routes are combined with affordable fares can public transport attract more drivers.')],
[('学业学习如何推进到生活水平？','知识提升专业准备与学业表现，扩大就业、薪资和晋升机会，进而支持生活水平。'),('社团活动提供哪些课堂理论难单独培养的技能？','在人际互动中练沟通、社交、组织与实践技能。'),('Only when放句首后主句如何排列？','Only when后的从句正常语序，主句用can等助动词加主语再加动词原形。')],
'换成员工培训，写两三句把专业学习与团队实践结合，使用Only when。','Technical courses can improve employees’ knowledge, while group projects develop communication skills. Only when formal learning is integrated with practical cooperation can training address both individual competence and teamwork.')
add('E06','Specialisation and a Broad Curriculum','同意程度题（大学课程广度）','按原稿大学课程设置理解：大学应保留广泛学科，同时重视专业化；通识能补强专业能力。',[
('开头：明确课程设置层面','题面a university should choose有歧义，本篇依原修订文讨论大学提供单一还是广泛学科；承认专业需求但支持课程广度。',['职业分化增加专业需求','提出大学集中一个学科','承认专业化价值','支持大学提供广泛学科']),
('专业化理由：集中投入','更多注意力投向一个领域可能提升学业，前沿专业知识帮助突破并支持职业发展；这些是专业化收益，尚不证明大学应删其他课程。',['集中努力与注意力','专业学术表现改善','前沿研究可能突破','知识密集社会职业发展受益']),
('反驳：通识服务专业','跨领域原理帮助理解已有知识并磨炼专业技能；书法课可能启发产品设计，说明广度与深度可互补，而非必然争夺价值。',['学习多领域基本原理','更好理解本专业知识','通识配合深入专业训练','专业任务与设计表现可能提高']),
('结尾：保留广度兼顾深度','大学保留通识教育，同时重视专业化；结论回应课程范围，没有把全篇改成学生只能选几个专业的不同问题。',['保留大学通识','重视专业深入','两者共同支持未来发展'])],
[('大学课程设置与学生选科不同',1),('前沿突破与职业阶梯搭配',1),('跨科例子不能写成必要条件',2)],
[
('the focused use of effort and attention','投入方式：the focused use of + 资源；focused指集中而非量最大。','The focused use of public funds can improve services on overcrowded bus routes.'),
('at the frontiers of knowledge','知识前沿：work/research at the frontiers of + 领域/knowledge。','Researchers at the frontiers of environmental science need to exchange ideas across disciplines.'),
('climb the career ladder','职业晋升：help + sb + climb the career ladder。','Communication skills can help employees climb the career ladder in international firms.'),
('can complement professional competence','互补关系：complement + N，不能加with作该动词宾语结构。','Experience of volunteering can complement the professional competence gained through formal study.'),
('equips them to sharpen their skills and knowledge','能力准备：equip + sb + to + V；sharpen + skills/knowledge。','Critical reading equips students to evaluate unfamiliar claims more carefully.')],
[('本文怎样处理题面大学选一个学科的歧义？','按原修订文讨论大学课程设置，应否提供广泛学科，而非擅自改成学生个人选科。'),('专业化有哪些收益，为什么还不足以排除其他学科？','集中投入可提升学业、科研与职业发展，但其他学科能补强理解和专业表现，二者可互补。'),('书法课例子说明什么，不说明什么？','说明更广学习可能启发产品设计；不证明所有跨科课程都保证提高专业成绩。')],
'换成企业只培训岗位技能还是加入沟通课程，用两三句说明补充学习如何服务专业表现。','Job-specific training can strengthen technical performance, but communication courses can complement professional competence. An engineer who explains problems clearly may coordinate repairs more effectively, so broader learning need not undermine specialisation.')

# Compile content; labels distinguish supplied corrections from retained reference expressions.
ref_text='\n'.join(p.read_text() for p in REF.glob('*.md')).replace('**','').replace('`','')
for record in records:
    d=D[record['code']].copy()
    notes=d.pop('notes'); correction_meta=d.pop('correctionMeta'); cols=d.pop('collocationData'); qa=d.pop('qa')
    record.update(d)
    record['paragraphNotes']=[dict(role=role,explanation=expl,chain=chain) for role,expl,chain in notes]
    for correction,(title,anchor) in zip(record['corrections'],correction_meta):
        correction['title']=title; correction['paragraphIndex']=anchor
    plain='\n\n'.join(record['essayParagraphs']).replace('**','')
    record['collocations']=[]
    for phrase,usage,example in cols:
        # Determine whether the selected occurrence overlaps a bold source edit.
        found=False; edited=False
        for paragraph in record['essayParagraphs']:
            clean=''; ranges=[]; in_bold=False; i=0
            while i<len(paragraph):
                if paragraph[i:i+2]=='**': in_bold=not in_bold; i+=2; continue
                if in_bold: ranges.append(len(clean))
                clean+=paragraph[i]; i+=1
            start=clean.find(phrase)
            if start>=0:
                found=True; edited=any(start<=j<start+len(phrase) for j in ranges); break
        assert found,(record['code'],'missing phrase',phrase)
        # Unbolded text is explicitly retained teacher text in the supplied source.
        label='校正' if edited else '熟悉（讲义）'
        record['collocations'].append(dict(phrase=phrase,source=label,usage=usage,example=example))
    record['questions']=[q for q,a in qa]; record['answers']=[a for q,a in qa]
    assert len(record['paragraphNotes'])==len(record['essayParagraphs']),record['code']
    assert len(record['corrections'])==3,record['code']
    assert 5<=len(record['collocations'])<=8,record['code']
    assert len(record['questions'])==len(record['answers'])==3,record['code']
    assert all(0<=c['paragraphIndex']<len(record['essayParagraphs']) for c in record['corrections'])
    assert all(c['revised'] in record['essayParagraphs'][c['paragraphIndex']].replace('**','') for c in record['corrections']), record['code']
    assert all(2<=len(n['chain'])<=5 for n in record['paragraphNotes']),record['code']
assert len(records)==28
assert set(D)=={r['code'] for r in records}
(ROOT/'data/eight.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print(f'Built {len(records)} records, {sum(len(r["essayParagraphs"]) for r in records)} exact paragraphs, {sum(len(r["corrections"]) for r in records)} corrections, {sum(len(r["collocations"]) for r in records)} collocations.')
