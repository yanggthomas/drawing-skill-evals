# 54 张图的盲评：人工评语与 Fable 评分

同样的 9 个 case × 3 个 arm 跑了两轮，全部做了盲评：10 月 1 日那轮（Claude Opus 带 / 不带绘图 skill，加上 `gpt-6-astra` + ImageGen），以及 10 月 4 日那轮（`gpt-5.6-sol` 带 skill / 不带 skill / ImageGen）。54 张 PNG 都在分支 `blind-scoring-54` 上做了匿名化（随机 token 命名，去掉 PNG 的附属数据块）。两位评审在不知道来源的情况下独立评审：

- **人工（你）：** 每张图写一段自由评语，见 [human-review.md](human-review.md)。
- **Fable 5.1（云端）：** 每张图打五个 1–5 分，评分细则由它自己细化（[RUBRIC-FINAL.md](fable-results/RUBRIC-FINAL.md)），并列出带出处的缺陷（[scores.json](fable-results/scores.json)、[REVIEW.md](fable-results/REVIEW.md)）。分支 `blind-scoring-54-results`，commit `2f4ca58`。

两边评审都完成之后，才把分数和私有的 [blind-key.json](blind-key.json) 对上。按你在 case 备注里的意见，**A3 不计入主要数字**：它是一张部署表格，不是架构图。全部 9 个 case 的数据见附录。

## 实验设置

### 9 个 case

| ID | Case | 题目要什么 | 当时期望的 skill |
|---|---|---|---|
| G1 | [vllm-v1-schedule](../../evals/vllm-v1-schedule/prompt.md) | vLLM V1 调度器的一个 step（控制流） | graphviz |
| G2 | [verl-ppo-step](../../evals/verl-ppo-step/prompt.md) | verl 的一个 PPO / GRPO 训练 step（多参与方步骤） | graphviz |
| G3 | [ffmpeg-transcode-threads](../../evals/ffmpeg-transcode-threads/prompt.md) | ffmpeg 转码的线程、队列、背压和输出同步 | graphviz |
| G4 | [redis-request-path](../../evals/redis-request-path/prompt.md) | Redis 一条请求在 client、主线程、I/O 线程之间的路径（时序） | graphviz |
| M1 | [megatron-tp-sp-mlp](../../evals/megatron-tp-sp-mlp/prompt.md) | Megatron TP + SP 下的 MLP 前向 / 反向 | model-architecture |
| M2 | [vllm-v1-mixed-batch-attn](../../evals/vllm-v1-mixed-batch-attn/prompt.md) | vLLM 混合批次的 attention 与 KV cache 分页 | model-architecture |
| A1 | [vllm-v1-process-arch](../../evals/vllm-v1-process-arch/prompt.md) | vLLM V1 单机 TP 服务的进程架构 | graphviz |
| A2 | [verl-resource-placement](../../evals/verl-resource-placement/prompt.md) | verl 的资源放置（worker 在 GPU 上的部署） | graphviz |
| A3 | [megatron-parallel-groups](../../evals/megatron-parallel-groups/prompt.md) | Megatron 并行组的成员关系（不计入主要数字） | graphviz |

每个 case 都给了钉住 commit 的源码，要求「每个元素都有代码依据」，交付一张 PNG。题目、answer key 和 grader 在 `evals/<case>/`。

### 两轮运行

| 轮次 | 运行 | 模型 | Arm | 协议 | 生产成本（9 张图） |
|---|---|---|---|---|---|
| 10 月 1 日 | [2026-10-01-skill-v0.1.0](../../runs/2026-10-01-skill-v0.1.0/README.md) | Claude Opus | skill（drawing-skills 0.1.0）、no-skill | Claude plugin eval | skill $9.63，no-skill $10.65 |
| 10 月 1 日 | [2026-10-01-codex-imagegen-v1](../../runs/2026-10-01-codex-imagegen-v1/README.md) | gpt-6-astra | ImageGen | 隔离的 Codex 会话，一次图像生成 | $10.94–$12.38 |
| 10 月 4 日 | [2026-10-04-gpt-5.6-sol-three-arm](../../runs/2026-10-04-gpt-5.6-sol-three-arm/README.md) | gpt-5.6-sol（high） | skill、no-skill、ImageGen | 隔离的 `codex exec`，提示词只有题目本身；ImageGen arm 多一句「用图像生成」 | skill $12.25，no-skill $8.74，ImageGen $8.82 |

每个格子只跑了一次（n = 1）。10 月 4 日那轮的 skill 读取、渲染命令和图像生成调用都从运行记录里核实过（见各 arm 的 `raw/` 证据）。

### 盲评流程

1. 54 张 PNG 统一改成随机 8 位 token 命名，去掉 PNG 的附属数据块（ImageGen 图里的 C2PA 签名、Graphviz 图里的背景和 DPI 块），像素数据不变；生成脚本是 [scripts/make_blind_set.py](../../scripts/make_blind_set.py)。
2. 匿名集放在单独的分支 `blind-scoring-54`，每个 case 附题目、answer key 和源码，不含任何来源信息。
3. 两位评审独立工作，都不知道每张图来自哪个模型、哪个 arm：
   - **人工评审**：每张图写自由评语；之后按方面编码（整体、内容、元素、布局、风格、图型），编码规则见下文「你的偏好」。
   - **Fable 5.1**：按五个维度各打 1–5 分（准确度、覆盖度、流程、可读性、视觉编码），总分 /25，技术分 = 总分 + 准确度（/30）；评分细则由它自己细化，每个缺陷都要给出源码出处。
4. 两边都完成后，才用 [blind-key.json](blind-key.json) 把 token 对回来源。
5. 在可比较的子项上，凡是两位评审强烈不一致，用人工判断替换 Fable 的分数，得到「校正后」的分数（规则见「校正后的分数」）。

### 本目录的文件

| 文件 | 内容 |
|---|---|
| [REPORT.md](REPORT.md) | 本报告 |
| [GALLERY.md](GALLERY.md) | 54 张图按 case 排列，附分数 |
| [scores.json](scores.json) | 结构化分数：10 月 4 日（`cases`）和 10 月 1 日（`oct01_cases`）各 9 个 case × 3 个 arm，含校正后的技术分和人工评语 |
| [human-review.md](human-review.md) | 人工评语原文 |
| [fable-results/](fable-results/) | Fable 的最终评分细则、逐图分数和评审报告 |
| [joined.json](joined.json) | 两位评审的分数、人工方面编码和校正结果，逐图合并 |
| [blind-key.json](blind-key.json) | token 到来源的对照表（评审完成后公开） |
| [comparison.yaml](comparison.yaml) | 归档清单 |

## 评审结论

> From my point of view, 最大的问题是graphviz不应该画很多时序图，我们skill也不会画时序。还有一个问题image gen天然在准确性，和易修改性上就要扣分。

这条结论是整份报告的基调。数据支持这两点：

- **Graphviz 被拿去画它画不好的多参与方密集时序。** G2（一个训练 step）和 G4（一条请求路径）问的是多个参与方之间一步一步发生了什么。Opus 的 skill arm 落后 no-skill 的技术分里，这两个 case 占了一半（−12 里的 −6）；`gpt-5.6-sol` 的 skill arm 落后的部分里，它们约占四分之一（−15 里的 −4）。这两个 case 里你选的「最好」都是 no-skill 画的时序图 / 泳道图（G2 `b22ede75`、G4 `a99b55ec`），你肯定的是图型合适（「时序图本身就很适合」）；整组里你最差评的 skill 图是 G4 的 Graphviz 图（`7d98c63e`）。目前没有任何 skill 提供泳道布局。G1（一个调度 step）不一样：它是单一主体的控制流，Graphviz 画得好（Opus `1eba22c4`，差距为 0）；`gpt-5.6-sol` 在 G1 上的差距（−5，`db0db3ff`）是布局失败，不是图型不匹配。
- **ImageGen 在准确性和可修改性上有天然的扣分，盲评分数低估了这一点。** 整组里三处实质性错误全部出自 ImageGen。而且没有一张 ImageGen 图留下可编辑的源文件，一根箭头画错，只能整张图重新生成，而重新生成又可能引入新错误。Fable 的评分细则里没有可修改性这一维，所以 ImageGen 在可读性上的优势在它的分数里没有被打折扣。

### 核心原则：关系和步骤要画出来，不要写出来

> **评审意见：** 之前所有失败的图，都是试图用图例、用文字替代图形来表达关系和步骤。

逐张核对之后，这条对内容和布局上的失败都成立：

| 失败的图 | 被写成文字的关系或步骤 |
|---|---|
| G3 `8c4c4637` 控制平面 | 调度器读什么、卡住谁，写在六边形里的段落中；下面还有三个孤立的说明框 |
| G3 `1bdb9dba`、A1 `9c82de56`、G4 `02d4d074` | 每个框文字太多：本该拆成多个框和边的结构，塞进了一个框 |
| M2 `8ff5963f`、`61583ee3` | poster 风格：用独立的文字面板逐段介绍步骤 |
| G4 `7d98c63e`、`8555a918` | 四个参与方的时序本该是生命线和消息，变成一条竖链加文字说明 |
| G2 `d46ecf7c` | driver 步骤和它调用的 worker 落在画布两端，对应关系只能靠编号和文字去找 |

有两类失败不在此列：风格失败（卡通配色、深色背景、大面积填色），以及 ImageGen 的「信息偏少」，后者的问题恰好相反，是细节丢了。

**正面对照：G1 `599e7123`。**（评审意见：虽然不喜欢它的风格，但关系是清楚的。）它的框里文字并不少，但关系和状态都画成了图形：
- 决策是菱形（「No preemption this step?」），YES / NO 两条边各通一个分支；
- 失败、重试、成功都是带标签的边：「Allocation failed」红线指向抢占，「Retry」虚线回到分配，「Success」「None → stop admission」各是一条边；
- 状态直接画出来：KV 块画成三组彩色格子（在用 / 前缀命中 / 新分配），8 个 token 预算格子里 A、B、C 各占几格一眼可见，分块预填充画成 10 个格子并切成「本步 4 个 + 剩余 6 个」。

所以判断标准不是文字多少，而是关系有没有画成图形：文字只说明节点，关系交给菱形、边和格子。

由此得到三条可操作的规则，在[下一轮计划](../../docs/benchmark-v2/README.md)里分别展开：
1. **不能有孤立节点**：每个节点都要通过边接到它解释的对象上。
2. **关系画成边**：「A 读取 B」「A 阻塞 C」里的 A、B、C 是节点，读取、阻塞是边，边上写动作或载荷；节点里只留名称和一两行说明。
3. **不依赖图例**：关系在图上就地标注，读者不看图例也能读懂；图例只做汇总。

这条原则也是 golden 和 grader 的核心检查项：评的是关系有没有画成图形，而不是框里有没有出现对应的词。

### 各 arm 保留可编辑源文件的情况

| Arm | 10 月 1 日 | 10 月 4 日 | 源文件类型 |
|---|---:|---:|---|
| skill | 9/9 | 9/9 | `.dot`（Graphviz）、`.tex`（TikZ） |
| no-skill | 7/9 | 7/9 | `.dot`、`.py`（matplotlib）、`.svg` |
| ImageGen | 0/9 | 0/9 | 无（只有位图） |

no-skill 缺的几份是没有存进运行归档的文件（10 月 1 日的 G4 和 A3；10 月 4 日的 G3 和 A2），不能证明当时没有源文件。

## 主要结论

1. **每个 arm 失分的方面都不一样，所以单一分数排不出高下。** 按你的评语，skill arm 内容最好（+7 / −1），框与框之间的排布最差（布局 −9）。no-skill 的主要问题是框里塞得太满（元素 −7），`gpt-5.6-sol` 还有深色主题的问题（风格 −5）。ImageGen 完全没有布局和元素方面的抱怨，但风格最差（−12），内容评价两极（+4 / −5，多半是「信息偏少」）。每张图只给一个数字，会把这些平均成几乎打平，把差异全部藏起来。
2. **在这次评测里，skill 没有赢过 no-skill 基线，只有 model-architecture 在 M1 上例外。** Fable 给 skill arm 的技术分比 no-skill 低 1.5 分（Opus）和 1.9 分（`gpt-5.6-sol`），输在流程和可读性上。原因有两个：多参与方的密集时序被画成了图（G2、G4）；图的规模远远超出 Graphviz skill 擅长的范围（20–30 个节点，而你 vault 里的中位数是 10，见建议部分）。在强冲突处用你的判断覆盖 Fable 之后，差距是 1.4 分和 0.9 分。两位评审都认可的 skill 明确胜出只有一处：M1，Opus 用 model-architecture 画的图，你说「应该是最好的，应该是得满分」，Fable 也把它放在最高档。
3. **skill 的弱点在框与框之间的布局，不在单个框的内容。** 你对 skill arm 的布局抱怨（−9）是所有 arm 里最多的，说的都是框怎么摆：连线乱、留白太多、横竖混排、一行摆不下拐弯。你对它的元素抱怨很少（−3）。Fable 在布局上和你一致：你批评过布局的图，Fable 可读性平均 2.92；你没提布局的图，平均 3.94。
4. **除了 ImageGen，正确性都接近满分。** 用代码渲染的 arm 准确度平均 4.9–5.0，没有实质性错误。整组三处实质性错误全部来自 ImageGen：两处在 A2 `cbd1fa32`（10 月 1 日），一处在 M1 `c87e8342`（10 月 4 日）。你把 A2 `cbd1fa32` 选为这个 case 里最清楚的图（「也应该说这幅图最清楚」），这正说明了风险：一张精致但箭头画错的图，会让读者信以为真。
5. **ImageGen 最好读，但不能当技术参考图用。** 它的 Fable 可读性最高（4.1–4.4），在 8 个主要 case 里拿了你 6 个「最好」中的 3 个。但所有实质性错误都在它身上，它不留可编辑源文件，按你的评语风格最差、内容最薄。在风格和内容深度上用你的判断覆盖 Fable 之后，ImageGen 的技术分从 27.1–27.4 降到 25.9，低于 no-skill，这还没算可修改性。
6. **Fable 在布局上和你一致，在风格上和你相反，对内容单薄视而不见。** 你不喜欢其风格的图，Fable 的视觉编码分平均 4.5，*反而高于*你没提风格的图（4.15）：Fable 奖励的正是你排斥的高饱和、卡通和深色风格。在内容上，你挑出毛病的七张图里，Fable 给了其中三张准确度 5 分：两张是「信息偏少」（它的覆盖度只看有没有，不看深度），另一张是 G2 `d46ecf7c`，你指出箭头方向错了，Fable 没有记录任何缺陷。换模型的影响小于换 arm：同一个 arm 里，10 月 1 日和 10 月 4 日的 Fable 分数很接近（skill 25.6 对 25.9，ImageGen 27.1 对 27.4）。

## 你的偏好：分方面统计

你的评语按方面编码，用的是你给出的区分：

| 方面 | 含义 | 典型说法 |
|---|---|---|
| 整体 | 对整张图的结论 | ⭐ 最好 / ✗ 最差、不合格 / + 一般性肯定（挺好、没啥问题） |
| 内容 | 完整度、深度、正确性，以及内容有没有清楚地传达出来 | 内容全 / 内容很清楚 / 信息偏少 / not tech enough / 箭头方向错 |
| 元素 | 单个框或箭头：文字多少、字号、框内文字排版、元素大小 | 每个box内容太多 / 字号偏小 / 箭头太大 / box偏大 |
| 布局 | 框与框怎么排：位置、连线、留白、遮挡、换行 | 排版 / 连线乱 / 遮挡 / 留白太多 / 横竖混排 / 一行摆不下 |
| 风格 | 配色、字体、观感 | 配色 / 卡通 / 鲜艳 / 深色 / 素雅 / 圆角字体 |
| 图型 | 图的形式是否适合要表达的机制 | 时序图很适合 / poster / 表格 / illustration |

每格统计正面和负面提及的次数；± 表示同一条评语在这个方面上有褒有贬。评语没提到的方面不填，也不算作中性。编码是我对你原话的理解；每条原始评语及其编码都在附录里。

| 轮次 | 模型 | Arm | 整体 | 内容 | 元素 | 布局 | 风格 | 图型 |
|---|---|---|---|---|---|---|---|---|
| 10 月 1 日 | Claude Opus | skill | 1⭐ | +5 / −1 | −2 | +1 / −4 | — | −1 |
| 10 月 1 日 | Claude Opus | no-skill | 1⭐ 2+ 1✗ | +1 / −1 | −4 | +1 / −2 | −1 | +1 / −1 |
| 10 月 1 日 | gpt-6-astra | ImageGen | 2⭐ 2+ | +2 / −3 | — | — | −6 | −1 |
| 10 月 4 日 | gpt-5.6-sol | skill | 2+ 2✗ | +2 (±1) | −1 | −5 | −2 | +2 / −1 |
| 10 月 4 日 | gpt-5.6-sol | no-skill | 1⭐ | — | −3 | −2 | +1 / −5 | +1 |
| 10 月 4 日 | gpt-5.6-sol | ImageGen | 1⭐ | +2 / −2 (±2) | — | +2 | −6 (±1) | −1 |
| **合计** | | **skill** | 1⭐ 2+ 2✗ | **+7 / −1** (±1) | −3 | +1 / **−9** | −2 | +2 / −2 |
| **合计** | | **no-skill** | 2⭐ 2+ 1✗ | +1 / −1 | **−7** | +1 / −4 | +1 / −6 | +2 / −1 |
| **合计** | | **ImageGen** | 3⭐ 2+ | +4 / −5 (±2) | — | +2 | **−12** (±1) | −2 |

**针对局部的评语信息量最大。** 好几条评语表扬一个区域、批评另一个区域，整图一个分数装不下：

- G3 `8c4c4637`（10 月 4 日 skill）：「data plane in this case best」；control plane「ok」；下面三个框「very confusing」；看不出控制平面和数据平面的交互；stream copy → `send_to_mux` 那个信号不清楚。分平面的布局思路是对的，执行不完整。
- G3 `d2237ccb`（10 月 1 日 skill）：排版更差、线更乱，但「控制模型比 8c4c4637 清楚」。G3 的两张 skill 图各赢一部分。
- A2 `89ec0612`（10 月 4 日 ImageGen）：配色太鲜艳，但「很喜欢左侧的 control plane」。
- G2 `d46ecf7c`（10 月 1 日 skill）：箭头方向错了，sleep replica 指向了 checkpoint engine。
- A1 `bba2c896`（10 月 1 日 ImageGen）：最右边两根箭头和左边不一致，容易看错。

## Fable 各 arm 评分（8 个 case）

| 轮次 | 模型 | Arm | 技术分 /30 | 总分 /25 | F | C | 流程 | 可读性 | 视觉 | 实质性错误 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 月 1 日 | Claude Opus | skill | 25.62 | 20.62 | 5.00 | 5.00 | 3.62 | 3.12 | 3.88 | 0 |
| 10 月 1 日 | Claude Opus | no-skill | 27.12 | 22.25 | 4.88 | 5.00 | 4.50 | 3.50 | 4.38 | 0 |
| 10 月 1 日 | gpt-6-astra | ImageGen | 27.12 | 22.75 | 4.38 | 4.88 | 4.50 | 4.38 | 4.62 | 2 |
| 10 月 4 日 | gpt-5.6-sol | skill | 25.88 | 20.88 | 5.00 | 5.00 | 4.12 | 3.00 | 3.75 | 0 |
| 10 月 4 日 | gpt-5.6-sol | no-skill | **27.75** | 22.75 | 5.00 | 5.00 | 4.50 | 3.62 | 4.62 | 0 |
| 10 月 4 日 | gpt-5.6-sol | ImageGen | 27.38 | 22.88 | 4.50 | 5.00 | 4.62 | 4.12 | 4.62 | 1 |

F = 准确度（Fidelity），C = 覆盖度（Coverage）。

### skill 减 no-skill，按 case 配对（Fable 技术分）

| 模型 | G1 | G2 | G3 | G4 | M1 | M2 | A1 | A2 | 平均 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Opus | 0 | −4 | −1 | −2 | **+2** | −2 | −3 | −2 | −1.50 |
| gpt-5.6-sol | −5 | −3 | +2 | −1 | −2 | −3 | −4 | +1 | −1.88 |

### Fable 和你一致的地方

| 你的方面 | 你挑出毛病的图数 | Fable 维度 | 这些图的 Fable 平均分 | 你没提的图的 Fable 平均分 |
|---|---:|---|---:|---:|
| 布局 | 13 | 可读性 | 2.92 | 3.94 |
| 布局 | 13 | 流程 | 3.62 | 4.61 |
| 元素 | 10 | 可读性 | 3.50 | 3.66 |
| 风格 | 20 | 视觉编码 | 4.50 | 4.15 |
| 内容 | 7 | 准确度 | 4.29 | 4.96 |

Fable 跟得上你对布局的判断，几乎察觉不到单个框过满，在风格上和你的判断相反，在内容上只部分一致。

## 校正后的分数：冲突处以你的判断为准

在可比较的子项上，凡是你和 Fable 强烈不一致的地方，用你的判断替换 Fable 的分数，仍用 Fable 自己的 1–5 分制。共改动 18 张图上的 20 个格子：

| 冲突 | 图数 | 规则 |
|---|---:|---|
| 你不喜欢风格；Fable 给视觉编码 5 分 | 15 | 视觉 → 3，即「有一个明显问题」那一档 |
| 你指出内容深度不够（「信息偏少」）；Fable 给覆盖度 5 分 | 3 | 覆盖度 → 3（M1 `c87e8342`、M2 `a58a7a4d`、`b9950cf1`） |
| 你判不合格（「Not what is required」）；Fable 给覆盖度 5 分 | 1 | 覆盖度 → 1，即「答非所问」那一档（M1 `04eed4f3`） |
| 你说箭头方向是「the major problem」；Fable 没记录缺陷 | 1 | 计为实质性错误：准确度封顶 3 分（G2 `d46ecf7c`） |
| 你认为交叉的线不碍事（「不影响阅读」）；Fable 给可读性 3 分 | 1 | 可读性 → 4（M2 `6fe5779e`） |

没有覆盖的：A2 `cbd1fa32`，你说它「最清楚」，Fable 按源码追出两处连线错误，给了准确度 2 分。清楚和正确是不同的子项，所以这不算正面冲突，Fable 的正确性分数保留。较弱的分歧（比如你抱怨了布局，而 Fable 给 4 分）按 Fable 原分保留。

| 轮次 | 模型 | Arm | Fable 技术分 | 校正后技术分 | 变化 | F | C | 流程 | 可读性 | 视觉 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 月 1 日 | Claude Opus | skill | 25.62 | 25.25 | −0.38 | 4.75 | 5.00 | 3.62 | 3.25 | 3.88 |
| 10 月 1 日 | Claude Opus | no-skill | 27.12 | 26.62 | −0.50 | 4.88 | 4.50 | 4.50 | 3.50 | 4.38 |
| 10 月 1 日 | gpt-6-astra | ImageGen | 27.12 | 25.88 | **−1.25** | 4.38 | 4.62 | 4.50 | 4.38 | 3.62 |
| 10 月 4 日 | gpt-5.6-sol | skill | 25.88 | 25.88 | 0.00 | 5.00 | 5.00 | 4.12 | 3.00 | 3.75 |
| 10 月 4 日 | gpt-5.6-sol | no-skill | 27.75 | **26.75** | −1.00 | 5.00 | 5.00 | 4.50 | 3.62 | 3.62 |
| 10 月 4 日 | gpt-5.6-sol | ImageGen | 27.38 | 25.88 | **−1.50** | 4.50 | 4.50 | 4.62 | 4.12 | 3.62 |

两轮合并，校正后的技术分是 no-skill 26.69、ImageGen 25.88、skill 25.56。ImageGen 降到 no-skill 以下，几乎和 skill arm 持平，这还没算可修改性。校正后 skill 减 no-skill：Opus −1.38（G2 −8，M1 +6），`gpt-5.6-sol` −0.88。

## 各 case 的最佳

| Case | Fable 最高（技术分） | 校正后最高 | 你选的最好 |
|---|---|---|---|
| G1 vLLM schedule | 10 月 4 日 no-skill `3f2ea037`（29） | 不变 | 10 月 1 日 ImageGen `599e7123`（「除了配色是最好的」）。你称赞 `3f2ea037` 配色「清晰、素雅」，但不喜欢它的大箭头 |
| G2 verl PPO step | 4 张并列 29：10 月 4 日 ImageGen、10 月 1 日 no-skill、10 月 4 日 no-skill、10 月 1 日 ImageGen | 并列 29：10 月 1 日 no-skill `b22ede75`、10 月 4 日 ImageGen `43118728` | 10 月 1 日 no-skill `b22ede75`（「时序图-like scheme best」） |
| G3 ffmpeg threads | 10 月 4 日 ImageGen `d9dc767f`（29） | 10 月 4 日 ImageGen `d9dc767f`（27） | 10 月 4 日 ImageGen `d9dc767f`（「应该最好」，但你不喜欢它的字体和配色）。局部：你认为 10 月 4 日 skill `8c4c4637` 的数据平面是这个 case 里最好的 |
| G4 Redis request path | 并列 29：10 月 4 日 ImageGen `7bd02c74`、10 月 1 日 ImageGen `b638523b` | 并列 28：10 月 4 日 no-skill `a99b55ec`、10 月 1 日 no-skill `02d4d074` | 10 月 4 日 no-skill `a99b55ec`（「最喜欢…时序图本身就很适合」）。校正后和最高分一致 |
| M1 Megatron TP+SP MLP | 并列 29：10 月 1 日 ImageGen、10 月 4 日 no-skill、10 月 1 日 skill `e0edfc5a` | 并列 29：10 月 1 日 skill `e0edfc5a`、10 月 1 日 ImageGen `1a297a07` | 10 月 1 日 skill `e0edfc5a`（「满分」） |
| M2 vLLM mixed-batch attention | 10 月 1 日 ImageGen `a58a7a4d`（30，唯一满分） | 10 月 1 日 no-skill `61583ee3`（29） | 无。你说 `a58a7a4d`「配色太卡通了。且信息偏少」 |
| A1 vLLM process architecture | 10 月 4 日 no-skill `2e3e34c4`（29） | 3 张并列 27：`2e3e34c4`、10 月 1 日 no-skill `9c82de56`、10 月 1 日 ImageGen `bba2c896` | 无。你肯定过的：`44dce42a`（10 月 4 日 skill，「挺好的」）、`0feeb41d`（10 月 4 日 ImageGen，布局） |
| A2 verl resource placement | 10 月 4 日 ImageGen `89ec0612`（27） | 不变 | 10 月 1 日 ImageGen `cbd1fa32`（「最清楚」）。**冲突：** Fable 在这张图里发现两处实质性连线错误（19 分，垫底）；没有覆盖，因为清楚不等于正确 |
| A3（不计入） | 并列 29：10 月 4 日 no-skill、10 月 1 日 no-skill | 未计算 | 10 月 1 日 ImageGen `73c5e8d6`（「整组最好」） |

## 成本

每个 arm 画 9 张图的生产成本（不含评审）。10 月 1 日的数字来自[之前的三 arm 报告](../2026-10-02-three-arm/REPORT.md)。10 月 4 日的数字来自运行审计，按官方 API 价格计算。ImageGen 的图像成本按高质量档计算，即每百万图像输出 token 30 美元。

| Arm | 10 月 1 日 | 10 月 4 日 |
|---|---:|---:|
| skill | $9.63 | $12.25 |
| no-skill | $10.65 | $8.74 |
| ImageGen | $10.94–$12.38 | $8.82（agent $6.74 + 15 次图像调用 $2.08） |

## 建议

*这些建议的展开（Claude Opus 与 Codex 的 skill 改进建议、下一轮测试集决定和 golden）见[下一轮计划：skill 改进与 benchmark v2](../../docs/benchmark-v2/README.md)。本报告只记录已完成的实验。*

1. **保留 Graphviz skill 的风格，教它画密集的图。** 它的配色、节点类别和声明式 DOT 源文件在日常使用里效果很好（vault 里 103 张图，中位数 10 个节点，文字 16 px）。这次评测要求的是一张 20–30 个节点的大而全的图，而每个模型的 8 个 case 里，no-skill 有 6 个处理得更好，说明密度问题是可以解决的。加一个规模检查：允许画多张图时，按问题拆分；要求只画一张时，用结构化单元格拼成多个面板。
2. **把已经奏效的模式写进 Graphviz skill。** 用一句话写明图要表达的论点；边标签写语义；用带编号的边表示顺序；cluster 只用来表示真实的边界；内容丰富的连接画成链路框；「阶段 × 负责方」网格；缩写说明；控制流就按控制流来画。
3. **用标准图型扩展 Graphviz skill。** 泳道图、UML 时序图、活动图、状态机、C4 容器图、数据流图和分层图，每种都用它为人熟知的画法，各配一个模板。简单的 UML（标签短、参与者少）用 Mermaid。复杂的时序和步骤流程，如果单元格内容丰富或每一步都带状态，用 PIL 泳道模板，它能从一个数据文件复现 G2 `b22ede75`。泳道图要有一套泳道配色，因为泳道是整块的区域；其他图型都沿用现在的配色。时间线和内存布局交给 TikZ。
4. **model-architecture 的张量流图只用于张量计算。** 它在 M1 上明确胜出。分页、块表和 rank 网格不要硬塞进张量流图，给它们一个内存 / 数组布局模板；时间线给一个甘特图模板，两者都用 TikZ。没有张量形状的概念说明图可以留在 Graphviz，vault 里那张 Q/K/V 图就是例子。
5. **明确给准确性和可修改性打分，ImageGen 只当插图用。** 以后的评分细则要加可修改性这一维，并逐根检查连线的两端。三处实质性错误都是精致的 ImageGen 图里箭头的端点画错了，其中一处骗过了细心的读者。
6. **分方面评审，以人工评审为主要依据。** 按方面收集反馈（内容、元素、布局、风格、图型），并附上针对局部的评语。如果要用自动评审，把你的风格偏好告诉它，并让它评内容深度。
7. **下一次评测两种情形都要测。** 保留「一张大而全的图」作为难度测试（它证明了密度可以处理得更好）；加入类似 vault 的 case，每张图只回答一个问题；替换 A3 和 M2；加入多参与方的密集 case，用来检验泳道和时序模板；每个 arm 跑两到三次。

## 附录：逐图结果

先按 case 排序，再按校正后的技术分排序。「Skill used」一列是实际用到的 skill，由运行记录（10 月 4 日）或 harness 指标（10 月 1 日）核实。「Reconciled」是在强冲突处用你的判断覆盖 Fable 之后的技术分（被覆盖的格子有标注，例如 V5→3）。「Your aspects」一列是你评语的方面编码：O 整体（⭐ 最好，✗ 最差 / 不合格，+ 肯定）、C 内容、E 元素、L 布局、S 风格、T 图型，各带 + / − / ±。分数列：F 准确度、C 覆盖度、Fl 流程、L 可读性、V 视觉编码。

| Case | Token | 轮次 | 模型 | Arm | 实际用到的 skill | F | C | Fl | L | V | 技术分 /30 | 校正后 | 覆盖 | 实质性错误 | 你的方面编码 | 你的评语 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---|
| G1 | `3f2ea037` | oct04 | gpt-5.6-sol | no-skill | none | 5 | 5 | 5 | 4 | 5 | 29 | 29 | — | 0 | E− S+ | 这一幅配色很清晰，也很素雅，但是箭头太大了。 |
| G1 | `599e7123` | oct01 | gpt-6-astra | imagegen | imagegen | 5 | 5 | 4 | 4 | 4 | 27 | 27 | — | 0 | O⭐ C+ S− | 应该说这一幅除了配色是最好的，内容也很清楚。只是整体有点卡通风。 |
| G1 | `28f89ba6` | oct04 | gpt-5.6-sol | imagegen | imagegen | 4 | 5 | 5 | 4 | 5 | 27 | 25 | V5→3 | 0 | C± S− | 这一幅比上一幅更清楚，但颜色比较鲜艳，而且左下角绿色的kv-block pool好像不太对应。 |
| G1 | `1eba22c4` | oct01 | claude-opus | skill | graphviz | 5 | 5 | 4 | 3 | 3 | 25 | 25 | — | 0 | C+ E− | generally ok, just to many works in each box. 整体几个阶段是比较清楚，kv-cache池也有表达。 |
| G1 | `6e033b2b` | oct01 | claude-opus | no-skill | none | 5 | 5 | 4 | 3 | 3 | 25 | 25 | — | 0 | E− S− | 这一幅也是内容太多了，配色一般吧，进一步加剧杂乱。 |
| G1 | `db0db3ff` | oct04 | gpt-5.6-sol | skill | graphviz | 5 | 5 | 4 | 2 | 3 | 24 | 24 | — | 0 | O✗ C+ L− | 应该说这个是排版最遭的一个，内容也还ok，但是横竖混排确实不太清楚。 |
| G2 | `43118728` | oct04 | gpt-5.6-sol | imagegen | imagegen | 5 | 5 | 5 | 4 | 5 | 29 | 29 | — | 0 | C± | this brings the question, is A,B,C dataproto perfectly in between 1-2, 2-3 and others. |
| G2 | `b22ede75` | oct01 | claude-opus | no-skill | none | 5 | 5 | 5 | 4 | 5 | 29 | 29 | — | 0 | O⭐ T+ | I like this 时序图-like scheme best. This would be best in this case. |
| G2 | `c320d4b7` | oct04 | gpt-5.6-sol | no-skill | none | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | E− S− | don’t lie the dark scheme. Also error to big. |
| G2 | `f5a313af` | oct01 | gpt-6-astra | imagegen | imagegen | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | O+ S− | don’t like the color scheme. good enough though. |
| G2 | `e125d79e` | oct04 | gpt-5.6-sol | skill | graphviz | 5 | 5 | 4 | 3 | 4 | 26 | 26 | — | 0 | O+ T+ | we can see this pic is trying to mini the multi column scheme, it is better though. but not as good as b22ede75. It is good enough though. |
| G2 | `d46ecf7c` | oct01 | claude-opus | skill | graphviz | 5 | 5 | 3 | 3 | 4 | 25 | 21 | F5→3 | 0 | C− | the major problem of this picture is direction of the arrow, for example, sleep replica is gen pointing to ckpt engine. |
| G3 | `d9dc767f` | oct04 | gpt-5.6-sol | imagegen | imagegen | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | O⭐ C+ L+ S− | 从信息含量和整体布局排版上，这一幅应该最好，但我不喜欢这种字体和配色。 |
| G3 | `1bdb9dba` | oct01 | claude-opus | no-skill | none | 5 | 5 | 4 | 3 | 4 | 26 | 26 | — | 0 | E− L+ | too many words in each box. although it shows the main flow clearly. |
| G3 | `8c4c4637` | oct04 | gpt-5.6-sol | skill | graphviz | 5 | 5 | 4 | 3 | 4 | 26 | 26 | — | 0 | C± L− T+ | : I like the data plane in this case best, it clearly shows the function, data and interaction with different queues.  The only thing to wonder is the part stream copy send packet ref/eof to send_to_mux, I may have question about this part. 确实没懂那里是个信号好事什么。 control panel drawing is ok, but the blow part is very confusing. 那三个不同的框。而且没看出control panel和 data panel的交互。 |
| G3 | `77c4b51b` | oct01 | gpt-6-astra | imagegen | imagegen | 4 | 4 | 5 | 5 | 5 | 27 | 25 | V5→3 | 0 | C− S− T− | this cartoon like style would be perfact for illustration, but not tech enough and lose too many detail and not serious enough, it seems. |
| G3 | `d2237ccb` | oct01 | claude-opus | skill | graphviz | 5 | 5 | 3 | 3 | 4 | 25 | 25 | — | 0 | C+ E− L− | 这个也还行吧，虽然排版没有另一个好，而且内容也偏多，确实这里更容易看出来 scheduler是中心。线会有点杂乱，但感觉控制模型比8c4c4637清楚。 |
| G3 | `d8edd397` | oct04 | gpt-5.6-sol | no-skill | none | 5 | 5 | 3 | 2 | 4 | 24 | 24 | — | 0 | L− | 这个就是线比较杂乱， 排版留白太多，不美观。 |
| G4 | `02d4d074` | oct01 | claude-opus | no-skill | none | 5 | 5 | 5 | 4 | 4 | 28 | 28 | — | 0 | O+ C+ E− | 这个挺好，挺清楚的，就是每个box内容太多，字号偏小。 |
| G4 | `a99b55ec` | oct04 | gpt-5.6-sol | no-skill | none | 5 | 5 | 5 | 4 | 4 | 28 | 28 | — | 0 | O⭐ S− T+ | 我觉得，除了黑色的背景和配色，应该说这一幅是我最喜欢，时序图本身就很适合吧。 |
| G4 | `7bd02c74` | oct04 | gpt-5.6-sol | imagegen | imagegen | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | C+ S− | 配色太鲜艳，其实内容是很清楚的。 |
| G4 | `b638523b` | oct01 | gpt-6-astra | imagegen | imagegen | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | S− | 我确实不喜欢这种卡通类型的配色。 |
| G4 | `7d98c63e` | oct04 | gpt-5.6-sol | skill | graphviz | 5 | 5 | 5 | 3 | 4 | 27 | 27 | — | 0 | O✗ S− | 这一个应该是我觉得skill里最糟糕的一张图，配色很有问题。特别是这些大的block |
| G4 | `8555a918` | oct01 | claude-opus | skill | graphviz | 5 | 5 | 4 | 3 | 4 | 26 | 26 | — | 0 | C+ L− T− | 内容是清楚的，但是一方面时排版的问题，另一方面是时序不是很清楚。 |
| M1 | `1a297a07` | oct01 | gpt-6-astra | imagegen | imagegen | 5 | 5 | 5 | 4 | 5 | 29 | 29 | — | 0 | O+ | good, nothing to comment. |
| M1 | `e0edfc5a` | oct01 | claude-opus | skill | model-architecture | 5 | 5 | 5 | 4 | 5 | 29 | 29 | — | 0 | O⭐ | 这一幅应该是最好的，应该是得满分。 |
| M1 | `4a7c14b4` | oct04 | gpt-5.6-sol | no-skill | none | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | E− S− | 箭头大小，每个block里文字的layout。以及不喜欢深色。 |
| M1 | `54a5fbd7` | oct04 | gpt-5.6-sol | skill | model-architecture | 5 | 5 | 4 | 4 | 4 | 27 | 27 | — | 0 | E− L− | 这一个主要还是有些box偏大，重叠了，而且一行没摆下，有拐弯不美观。 |
| M1 | `04eed4f3` | oct01 | claude-opus | no-skill | none | 4 | 5 | 5 | 4 | 5 | 27 | 23 | C5→1 | 0 | O✗ C− | Not what is required. fail. |
| M1 | `c87e8342` | oct04 | gpt-5.6-sol | imagegen | imagegen | 3 | 5 | 4 | 5 | 4 | 24 | 22 | C5→3 | 1 | C− S± T− | image gen的图，配色比较卡通，也喜欢圆角字体。比较适合演示，但同样，信息量没有skill的更大，更全面。 |
| M2 | `61583ee3` | oct01 | claude-opus | no-skill | none | 5 | 5 | 5 | 4 | 5 | 29 | 29 | — | 0 | O+ T− | 其实我不是很喜欢这种poster-like的感觉。虽然这幅图实际没啥问题。其实这个case不是model architecture cover的范围，他不属于模型结构。当然也还ok。 |
| M2 | `6fe5779e` | oct01 | claude-opus | skill | model-architecture | 5 | 5 | 4 | 3 | 5 | 27 | 28 | L3→4 | 0 | L+ | 这个一样的，我觉得倒是不影响阅读。中间的线。本身也表达，kv cache的存储顺序是乱的。 |
| M2 | `85ac7bde` | oct04 | gpt-5.6-sol | no-skill | none | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | S− | 配色不好，橙色，深绿太高饱和了。 |
| M2 | `a58a7a4d` | oct01 | gpt-6-astra | imagegen | imagegen | 5 | 5 | 5 | 5 | 5 | 30 | 26 | V5→3, C5→3 | 0 | C− S− | 配色太卡通了。且信息偏少 |
| M2 | `8ff5963f` | oct04 | gpt-5.6-sol | skill | model-architecture | 5 | 5 | 4 | 3 | 4 | 26 | 26 | — | 0 | C+ L− T− | 其实就是我说的，这个图本身有连线遮挡的问题，但内容是全的，但我整体不喜欢这种poster风格。一个图，介绍所有步骤。而且这个case不适合m skill |
| M2 | `b9950cf1` | oct04 | gpt-5.6-sol | imagegen | imagegen | 5 | 5 | 5 | 4 | 5 | 29 | 25 | V5→3, C5→3 | 0 | C− S− | 配色太卡通了。且信息偏少 |
| A1 | `2e3e34c4` | oct04 | gpt-5.6-sol | no-skill | none | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | S− | 这个也差不多，但主要问题还是配色。 |
| A1 | `9c82de56` | oct01 | claude-opus | no-skill | none | 5 | 5 | 4 | 3 | 5 | 27 | 27 | — | 0 | E− L− | 这个内容就太多了，而且排版问题很大。 |
| A1 | `bba2c896` | oct01 | gpt-6-astra | imagegen | imagegen | 4 | 5 | 4 | 5 | 5 | 27 | 27 | — | 0 | C− | 这个也没啥大问题。就是最右边有两个箭头和左边不一致，容易引起误解。 |
| A1 | `0feeb41d` | oct04 | gpt-5.6-sol | imagegen | imagegen | 4 | 5 | 4 | 4 | 4 | 25 | 25 | — | 0 | L+ S− | 配色太卡通了。但整体布局我很喜欢， 很清楚。 |
| A1 | `44dce42a` | oct04 | gpt-5.6-sol | skill | graphviz | 5 | 5 | 4 | 3 | 3 | 25 | 25 | — | 0 | O+ | 这个也没啥问题，挺好的。 |
| A1 | `fd86cbc4` | oct01 | claude-opus | skill | graphviz | 5 | 5 | 3 | 3 | 3 | 24 | 24 | — | 0 | C+ L− | 排版不好，但其实内容是最全的。但是内容最清楚。 |
| A2 | `89ec0612` | oct04 | gpt-5.6-sol | imagegen | imagegen | 5 | 5 | 4 | 4 | 4 | 27 | 27 | — | 0 | S− | 配色太鲜艳了，我很喜欢左侧的control plane。 |
| A2 | `49f8027c` | oct04 | gpt-5.6-sol | skill | graphviz | 5 | 5 | 4 | 3 | 4 | 26 | 26 | — | 0 | L− S− | 这个第一是连线很乱，同时右下角的global pool几个大的填色block，很丑。不美观。 |
| A2 | `6eed9fef` | oct01 | claude-opus | no-skill | none | 5 | 5 | 4 | 3 | 4 | 26 | 26 | — | 0 | L− | 这个就比较乱了，当然layout 很不好。 |
| A2 | `3223b16a` | oct04 | gpt-5.6-sol | no-skill | none | 5 | 5 | 3 | 3 | 4 | 25 | 25 | — | 0 | L− | 这个主要是连线遮挡内容。 |
| A2 | `208d31f6` | oct01 | claude-opus | skill | graphviz | 5 | 5 | 3 | 3 | 3 | 24 | 24 | — | 0 | C+ L− | 这幅也是清楚的，就是连线太乱看不清，而且布局不太好。 |
| A2 | `cbd1fa32` | oct01 | gpt-6-astra | imagegen | imagegen | 2 | 5 | 3 | 4 | 3 | 19 | 19 | — | 2 | O⭐ C+ S− | 也应该说这幅图最清楚。除了配色和字体。 |
| A3 | `1daf798b` | oct01 | claude-opus | skill | graphviz | 5 | 5 | 4 | 4 | 5 | 28 | 28 | — | 0 | L− | 布局不太好。 |
| A3 | `a00afc4a` | oct04 | gpt-5.6-sol | imagegen | imagegen | 5 | 5 | 4 | 4 | 5 | 28 | 28 | — | 0 | L+ T± | 同样的表格，排版好一些吧。 |
| A3 | `cabeeecb` | oct04 | gpt-5.6-sol | no-skill | none | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | L+ S− | 不喜欢黑色背景，但整体布局挺好。 |
| A3 | `cca705dc` | oct01 | claude-opus | no-skill | none | 5 | 5 | 5 | 4 | 5 | 29 | 27 | V5→3 | 0 | S− | 配色太丑了 |
| A3 | `73c5e8d6` | oct01 | gpt-6-astra | imagegen | imagegen | 4 | 5 | 5 | 5 | 4 | 27 | 27 | — | 0 | O⭐ | 这个可能整组最好吧。 |
| A3 | `c8fcd33b` | oct04 | gpt-5.6-sol | skill | graphviz | 5 | 5 | 4 | 4 | 4 | 27 | 27 | — | 0 | T− | 表格形式就是差强人意吧。 |
