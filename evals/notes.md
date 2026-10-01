**一句话：** 前两轮测的大多是 **graphviz skill 设计范围之外的题**（流程/时序）。在这些题上 skill **没让评分更高**（readability 输了 1 个 case，平均 Δ = −0.11），但让 agent **更快、更省、风格更统一**。graphviz 的主场（架构图）放到第 3 轮 A1–A3 去测。

1. **题型和 skill 不对口是主因。** graphviz skill 的模板、7 种语义节点（primary 系统、tool 存储、muted 外部依赖……）和自动布局，都是为了表达"由什么组成、怎么连接"。G1（单步算法）、G2（训练步骤顺序）、G4（跨线程请求生命周期）问的是"先做什么、后做什么、谁交给谁"，本质是流程图 / 时序图。SKILL.md 自己写着 "Not for UML sequence / activity"，但描述里的 "runtime data flow" 让这些题全部触发了它（4/4）。
   - 结果：带 skill 的图都被模板拉成"一条竖直主干 + 旁边分区"的拓扑布局，回边和跨组的边横穿全图。不带 skill 的组更自然地画成泳道、按步骤排的表格或横向流水线（G2、G3、G4），评委更喜欢。
   - G3 是混合题：线程和队列的拓扑在 skill 范围内，背压和 DTS 同步是动态行为。这是唯一一个带 skill 输掉 readability 的 G 类 case。
2. **correctness 已经饱和。** 12 张图 12 张通过（全部 3:0）。Opus 不带 skill 也能读透源码、画全要点，所以 Δ 只来自 readability。
3. **model-architecture 在自己的范围内表现合格。** M1、M2 都正确路由到它并改走 TikZ。M1 是这批图里最像论文插图的一张。M2 输在"写 KV"那一段有十几条交叉弯箭头；不带 skill 的组用"每个 block 一行 + 文字标注槽位"代替连线，更干净。
4. **效率：graphviz 模板在范围外也有效。** G 类 4/4 个 case 带 skill 都更快、更便宜：平均 136 秒 vs 248 秒（−45%），$1.04 vs $1.20（−13%）；耗时可预测性 0.83 vs 0.53。M 类相反：TikZ 要写更多代码、还要编译，带 skill 258 秒 / $1.36，不带 skill 203 秒 / $1.12。
5. **风格一致性：graphviz 的配色模板很稳。**
   - G 类跨 case 的色相相似度：带 skill 0.67，不带 skill 0.52。
   - 同一题（G1）画两次：带 skill 0.93，不带 skill 0.58。
   - M 类两组都在 0.42–0.43：model-architecture 没有统一的色板。
6. **质量一致性差不多。** G 类 0.71 vs 0.67；Claude 看图均分带 skill 4.2、不带 skill 4.4。带 skill 在 G 类"版式清晰"四个都是 3 分：很稳定，但稳定在偏低的位置，这正是模板不适合流程题的表现。

**下一步：**
- 第 3 轮跑 A1–A3 架构题，看 graphviz skill 在主场上能不能把 readability 也赢回来。
- 按 [SKILL-IMPROVEMENTS.md](SKILL-IMPROVEMENTS.md) 强化 skill，再用同样的 9 个 case 做"旧 skill / 新 skill / 无 skill"三组对比。

**局限：** 每个 case 每组只跑了 1 次；G1 跑过三次，带 skill 组的 readability 结果就翻转过一次，看趋势比看单个数字更有意义。评委和看图评分都是模型给出的；人工美观打分（PLAN 第 9 步）还没做。前两轮总花费：冒烟 $3.18 + G1 正式 $2.12 + 第 2 轮 $13.95 = **$19.25**（含评委）。
