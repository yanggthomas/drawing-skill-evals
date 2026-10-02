# 强化 graphviz / model-architecture skill 的方案

依据：前两轮 6 个 case 的评分、trace 和最终图（见 [REPORT.md](../REPORT.md)）。核心发现是 **graphviz skill 只有一套"架构拓扑"画法，但用户的日常问题里有一大半是流程和时序**。skill 没有拒绝这类题，也没有换一套画法，于是把流程题硬套进拓扑布局，readability 因此吃亏。

下面按优先级排列。每条都写了"证据 → 改什么 → 怎么验证"。

---

## P0 · 先判断图的类型，再选模板（graphviz）

**证据：** G1/G2/G4 都是流程或时序题，4/4 触发了 graphviz，全部用 `style-template.dot`（拓扑模板），版式清晰都只拿到 3/5。不带 skill 的组自己选了泳道（G4）、步骤×角色表格（G2）、横向流水线卡片（G3），评委更喜欢。

**改什么：** 在 SKILL.md 的 Workflow 第 1 步之前加一个"图类型判定"：

| 问题在问什么 | 图类型 | 模板 | 布局要点 |
|---|---|---|---|
| 由哪些组件组成、怎么连接、部署在哪 | 架构 / 拓扑 | `style-template.dot`（现有） | 现有规则不变 |
| 多个参与者（线程、进程、服务）之间按时间交接 | **泳道** | 新增 `swimlane-template.dot` | 每个参与者一个 `cluster`，用 `rank=same` 和不可见边把同一时刻的节点对齐；共享队列单独放在两条泳道之间；步骤编号①②③… |
| 单个参与者内部的算法 / 循环 / 分支 | **流程图** | 新增 `flowchart-template.dot` | 上→下单一主干；判断用菱形；循环回边设 `constraint=false` 并贴着主干走；侧边说明框用 `rank=same` 挂在对应步骤旁，不让它们拉长布局 |
| 按步骤 × 角色的数据流（训练循环、pipeline 阶段） | **步骤矩阵** | 新增 HTML-label 表格模板 | 行 = 步骤，列 = 角色 / 进程；单元格里写"谁做了什么"，最右列写数据的变化 |

同时把 description 里的 "runtime data flow" 改成更明确的说法，例如："architecture, topology and runtime data-flow between components; for step-ordered processes use the swimlane / flowchart / step-matrix templates in this skill"。这样触发范围不变，但会走对的模板。

**怎么验证：** G1 应选流程图模板，G2 选步骤矩阵，G4 选泳道，G3 选拓扑 + 泳道；A1–A3 仍然选拓扑模板。在 trace 里检查 agent 读的是哪个模板文件（`collect.py` 已经记录了 Read 调用）。

## P0 · 可读性预算：图要在缩小后仍然看得清

**证据：** 12 张图里 6 张 readability 没通过。原图长边 3000–4000 px，评委看到的是长边约 2000 px 的 JPEG；节点里塞满 `file:line` 和多行公式，缩小后字只有几个像素高。带 skill 的 G4 图是 4001×1955，是最宽的一张。

**改什么：** 在 SKILL.md 加一节"可读性预算"，写成硬性规则：
- 图的长边 ≤ 2400 px：`graph [dpi=150, size="16,16"]`；超出时先拆图或精简，而不是缩小字号。
- 节点标签最多 4 行，每行 ≤ 50 个字符；正文字号 ≥ 11 pt。
- `file:line` 引用不放进节点正文：在节点里只留短编号（如 `[S3]`），完整的 `file:line` 统一列在图下方的"来源"表里。
- 一张图里跨 cluster 的长边不超过 3 条；超过就重新分组，或改用泳道 / 矩阵布局。

**怎么验证：** `collect.py` 记录 PNG 尺寸；readability 通过率应该上升，同时 correctness 不下降（行号挪到图例后，评委仍能看到）。

## P1 · 让渲染后的自检对准扣分点

**证据：** 两组其实都会自检：每次运行都用 Read 查看 PNG 1–6 次，并重新渲染 1–6 次（带 skill 的 G2、G3 各看了 4 次）。但最终交出的图里，横穿全图的长边和缩小后看不清的小字仍然在，而这两项正是 readability 扣分的原因。说明自检没有对准这两项。不带 skill 的 G3 自检了 6 次、用了 442 秒，说明没有上限的自检也很贵。

**改什么：** 在 Workflow 加第 5 步："渲染后用 Read 打开 PNG，按这份清单检查：① 长边是否 ≤ 2400 px；② 按缩小一半的效果估计，最小的字是否还能看清；③ 有没有横穿全图或跨越 2 个以上 cluster 的边；④ 阅读方向是否单一；⑤ 有没有重叠。任何一项不满足就修改，**最多改 2 轮**。"

**怎么验证：** readability 提升，同时 G 类的耗时优势（目前 −45%）基本保留，例如耗时增幅控制在 +20% 以内。

## P1 · model-architecture：逐元素的表格少用连线

**证据：** M2 带 skill 那张图在"写入 KV cache"一段，用十几条弯箭头把 token 连到 cache 槽位，箭头彼此交叉，readability 0:3。不带 skill 的组改成"每个 block 一行，格子里直接标出 token 编号"，3:0。

**改什么：** 在 `references/figure-grammar.md` 加一条：逐 token、逐槽位的映射用"同色编码 + 格内标注"来表达，不用连线；一张图里的连线不超过 6 条。另外提供一个 TikZ `matrix` 网格模板（行 = 请求或 block，列 = 位置，每个请求固定一种颜色）。

**怎么验证：** M2 的 readability 通过；M1 的论文风格不受影响。

## P2 · model-architecture：减少 TikZ 的耗时

**证据：** M 类带 skill 平均 258 秒 / $1.36，不带 skill 203 秒 / $1.12。trace 里的多轮"改 `.tex` → 编译 → 报错 → 再改"占了大部分时间。

**改什么：** 提供一个预编译过的 preamble（常用 `tikz` 库、颜色、节点样式都定义好），并附一份"常见编译错误和修法"的速查表（例如 `&` 转义、`matrix` 里的 `\\`、中文字体）。`render.sh` 在编译失败时只打印第一条错误。

**怎么验证：** M 类带 skill 的耗时降到不高于不带 skill。

## P2 · 新增一个时序图入口（可选）

**证据：** G4 是标准的 UML 时序图题，SKILL.md 也把时序图交给 Mermaid，但插件里没有 Mermaid 相关的 skill，所以实际上还是走了 graphviz。

**改什么：** 二选一：
- (a) 新增一个轻量的 `sequence` skill，用 Mermaid `sequenceDiagram` 通过 `mmdc` 渲染，前提是你常用的环境里有 `mmdc`；
- (b) 不加新 skill，靠 P0 的泳道模板覆盖这类题。

我倾向 **(b)**：少一个依赖，而且泳道模板在 Graphviz 里能沿用同一套语义配色，保住目前风格一致性上的优势。

---

## 建议的验证方式

1. 先跑第 3 轮 A1–A3（现有 skill），确认 graphviz 在架构题上的基线。
2. 按 P0 和 P1 修改 skill，作为 v0.2。
3. 用全部 9 个 case 跑三组：v0.1、v0.2、无 skill，每组 1 次。`claude plugin eval` 原生只支持带插件 / 不带插件两组，所以 v0.1 和 v0.2 分两次运行，或者把 v0.1 复制成另一个插件目录。
4. 重点看四项：
   - 流程/时序类的 readability 是否追平或超过无 skill；
   - 架构类是否保持领先；
   - 耗时优势是否保留；
   - 风格一致性是否保持在 ≥ 0.65。
