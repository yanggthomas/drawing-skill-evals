**一句话：** skill 让 agent **更快、更省、风格更统一**（G 类明显），路由也全部正确；但这一轮**评分并没有更高**：correctness 两组都满分，readability 上不带 skill 的组反而赢了 2 个 case，平均 Δ = −0.11。

1. **correctness 已经饱和。** 12 张图 12 张通过（全部 3:0）。Opus 不带 skill 也能把源码读透，并把答案要点画全，所以这个评分器在本题集上区分不了两组。Δ 完全来自 readability。
2. **readability：带 skill 2/6，不带 skill 4/6。** 输掉的 G3、M2 有共同点：
   - 带 skill 的 Graphviz 模板倾向于"一条竖直主干 + 旁边的分区"，控制流和回边要横穿全图，长边、交叉边多；M2 的 TikZ 图在"写入 KV"那一段有十几条交叉弯箭头。
   - 不带 skill 的组更常画成**网格 / 泳道 / 卡片**（G2、M2 用 Pillow 逐格画表，G3 用横向 record 卡片），阅读方向单一，交叉少，评委更喜欢。
   - 两组都有一个共同扣分点：节点里塞满 `file:line` 小字，原图 3000–4000 px，评委看到的是缩到约 2000 px 的 JPEG，小字不可读。
3. **skill 路由 6/6 正确，无误用。** G 类都调用 `graphviz`，M 类都调用 `model-architecture` 并改走 TikZ。不带 skill 时，M1 画成了 Graphviz 流程图，M2 用 Pillow 自己画。skill 确实改变了画图路线。
4. **效率：G 类带 skill 明显更快、更省、更可预测。**
   - G 类 4/4 个 case 带 skill 都更快、更便宜：平均 136 秒 vs 248 秒（−45%），$1.04 vs $1.20（−13%）。耗时可预测性 0.83 vs 0.53，不带 skill 的 G3 一次用了 442 秒。
   - M 类相反：TikZ 路线写得多、要编译，带 skill 平均 258 秒 / $1.36，不带 skill 203 秒 / $1.12。
   - 全部 6 个 case 合计：带 skill 1060 秒 / $6.87，不带 skill 1395 秒 / $7.05。
5. **风格一致性：skill 让配色更统一，但只在 graphviz 类明显。**
   - G 类跨 case 的色相相似度：带 skill 0.67，不带 skill 0.52。
   - 同一题（G1）重复画两次：带 skill 0.93，不带 skill 0.58。可以看出 graphviz skill 的配色模板（紫色步骤、黄色判断、圆柱存储、红色异常）每次都会复现。
   - M 类两组都在 0.42–0.43。model-architecture skill 没有强制统一的色板，每张 TikZ 图的配色都是按内容重新设计的。
6. **质量一致性差不多。** G 类 0.71 vs 0.67，M 类 0.67 vs 1.00（M 类只有 2 个 case）。Claude 看图均分：带 skill 4.2，不带 skill 4.4。带 skill 在 G 类的"版式清晰"四个都是 3 分，打分很稳定，但是稳定在偏低的位置。

**对 skill 的改进建议**（从输掉的 case 归纳）：
- graphviz skill 加一段"版式"指引：有多个参与者时优先用**泳道**（`rank=same` + 每个参与者一个 cluster），回边用 `constraint=false` 并尽量缩短，避免一条竖直主干加四周分区的布局。
- 节点标签里少放 `file:line`，把行号挪到图例或脚注；控制输出尺寸（例如长边 ≤ 2400 px），保证缩小后字还能看清。
- model-architecture skill 对"逐 token / 逐槽位"的表格类图，用网格加颜色编码代替大量连线。

**局限：** 每个 case 每组只跑了 1 次；G1 的三次运行里带 skill 的 readability 结果就翻转过一次，所以单个 case 的 Δ 不可靠，看趋势比看单个数字更有意义。评委和看图评分都是模型给出的；人工美观打分（PLAN 第 9 步）还没做。本次评测总花费：冒烟 $3.18 + G1 正式 $2.12 + 第 2 轮 $13.95 = **$19.25**（含评委）。
