# 2026-10-01 · drawing-skills v0.1.0 A/B 评测（归档）

> ⚠ **这次评测的设计存在问题，分数和 Δ 不能用来判断 skill 的好坏。** 原因见 [LIMITATIONS.md](LIMITATIONS.md)。可以采信的部分是路由、效率（agent 耗时和花费）、定性观察，以及完整保存的产物。

## 被测对象

| 项 | 值 |
|---|---|
| 插件 | `drawing-skills` 0.1.0（`.claude-plugin/plugin.json`） |
| skill 版本 | `skills/` 最后修改提交 `b98f1a4`，tree `3bd0fe709485`；评测期间**没有修改** |
| skill | `graphviz`、`model-architecture` |
| 工具 | `claude plugin eval`（Claude Code 2.1.286），每个 case 带插件 / 不带插件各 1 次 |
| agent / 评委 | Opus / Opus |
| 授权 | `--allow-tools Write Bash`（Bash 在 bubblewrap 沙箱中运行） |
| 环境工具 | Graphviz、Mermaid CLI、LaTeX/TikZ、matplotlib、Pillow、ImageMagick（`cloud-setup.sh`） |

## 运行记录

| 运行 | case | 结果 JSON | HTML 报告 | claude.ai 报告 | 花费 |
|---|---|---|---|---|---|
| 冒烟 1 | G1，只跑带 skill 组 | [results/smoke1-g1-with-only.json](results/smoke1-g1-with-only.json) | [html/smoke1-g1.html](html/smoke1-g1.html) | — | $0.71 |
| 冒烟 2 | G1 | [results/smoke2-g1.json](results/smoke2-g1.json) | [html/smoke2-g1.html](html/smoke2-g1.html) | https://claude.ai/artifact/48eGkUccJApgXXyzHULkoC | $2.47 |
| 第 1 轮 | G1 | [results/round1-g1.json](results/round1-g1.json) | [html/round1-g1.html](html/round1-g1.html) | https://claude.ai/artifact/Uv7DAEmc1ScSDodcRYTin3 | $2.12 |
| 第 2 轮 | G2 G3 G4 M1 M2 | [results/round2.json](results/round2.json) | [html/round2.html](html/round2.html) | https://claude.ai/artifact/59ygTcjybaK2g3Am93ScF4 | $13.95 |
| 第 3 轮 | A1 A2 A3 | [results/round3-arch.json](results/round3-arch.json) | [html/round3-arch.html](html/round3-arch.html) | https://claude.ai/artifact/CnZsXTdzUqtuU1giDirJdu | $7.21 |

冒烟 1 的 Bash 授权只放行了以 `dot` 开头的命令，所以没有生成 PNG，只用来排查问题。总花费 **$26.46**（含评委）。

## 目录

- [REPORT.md](REPORT.md)：汇总报告，包含每个 case 的详情和两组画出的图（由 `scripts/make_report.py` 生成）
- [LIMITATIONS.md](LIMITATIONS.md)：评测设计的问题
- [notes.md](notes.md)：总体观察，包含人工评价
- [SKILL-IMPROVEMENTS.md](SKILL-IMPROVEMENTS.md)：skill 强化方案（**未实施**，按用户决定不修改 skill）
- `results/`：每次运行的 `--json` 输出
- `html/`：每次运行的 HTML 报告
- `cases/<case>/`：
  - `artifacts/{with,without}-1/`：最终 PNG、源码（.dot / .tex / .py）、压缩后的 trace
  - `artifacts/runs.json`、`summary.json`：只算 agent 本身的耗时、花费、轮数，以及画图路线和越界读文件检查（由 `scripts/collect.py` 生成）
  - `review.json`：Claude 看图评分；`content-review.json`：逐子问题的内容可读性；`notes.md`：观察

case 定义（prompt、答案要点、评分器、复制进来的源码）在仓库的 `evals/<case>/`，不随这次运行变化。
