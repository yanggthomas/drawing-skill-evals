# 下一轮测试集的 golden

评审决定的 7 个 case，每个 case 一张 golden 图。golden 只用来校准评审和写 grader，绝不给生成方看。已有合格的图就直接复用；没有的才新画。7 张 golden 都放在 [goldens/](goldens/)：新画和复刻的只保留源文件和最终的 PDF、PNG；复用的是原图的逐字节副本。

| Case | 考的图型 | Golden | 来源 |
|---|---|---|---|
| G2 verl PPO step | 泳道图 | [g2-ppo-step.png](goldens/g2-ppo-step.png)（[源文件](goldens/g2_ppo_step.py)，引擎 [swimlane.py](goldens/swimlane.py)） | 复刻 10 月 1 日 no-skill 的 [`b22ede75`](../../runs/2026-10-01-skill-v0.1.0/cases/verl-ppo-step/arms/without/ppo-step.png)，像素差 0.14%，内容可编辑 |
| G3 FFmpeg 转码线程 | 管线 + 控制器 | [g3-transcode-threads.png](goldens/g3-transcode-threads.png)（[源文件](goldens/g3_transcode_threads.py)） | 新画：数据平面参考 `8c4c4637`，布局参考 `d9dc767f`，调度器画成结构参考 `d2237ccb` |
| M1 Megatron TP+SP MLP | 张量计算 | [m1-tp-sp-mlp.png](goldens/m1-tp-sp-mlp.png)（[源文件](goldens/m1-tp-sp-mlp.tex)） | 直接复用 10 月 1 日 skill 的图 [`e0edfc5a`](../../runs/2026-10-01-skill-v0.1.0/cases/megatron-tp-sp-mlp/arms/with/tp-sp-mlp.png)，评审给「满分」 |
| A1 vLLM 进程架构 | 部署图 | [a1-process-arch.png](goldens/a1-process-arch.png)（[源文件](goldens/a1_process_arch.py)） | 新画：布局参考 `2e3e34c4`，徽标编号对应 answer key 事实 |
| MLA | 张量计算 | [mla.png](goldens/mla.png)（[源文件](goldens/mla.tex)） | 新画：参考 tensor_dsl 的 MLA 图手改 TikZ，省略标准 attention，突出低秩 Q / KV、解耦 RoPE 和 KV cache（`c^KV` + `k^R`） |
| Mooncake 栈 | 分区拓扑 | [mooncake-stack.png](goldens/mooncake-stack.png) | 直接复用 vault 里认可的图（[approved-vault-examples/](approved-vault-examples/) 的副本），没有源文件 |
| Ray 对象数据路径 | 分支的数据路径 | [ray-object-data-path.png](goldens/ray-object-data-path.png) | 直接复用 vault 里认可的图（[approved-vault-examples/](approved-vault-examples/) 的副本），没有源文件 |

G3、A1 题目不变，只修订 golden，所以已有的 12 张图可以用新 golden 重新打分，作为 golden 的校准测试。MLA、Mooncake 栈和 Ray 是新 case，还要按 golden 写题目、answer key 和 grader。

## 重新生成

```bash
cd goldens
~/.uve/model_viz/bin/python a1_process_arch.py      # → a1-process-arch.png / .pdf
~/.uve/model_viz/bin/python g3_transcode_threads.py # → g3-transcode-threads.png / .pdf
~/.uve/model_viz/bin/python g2_ppo_step.py          # → g2-ppo-step.png / .pdf
pdflatex mla.tex && pdftoppm -png -r 200 -singlefile mla.pdf mla && rm mla.aux mla.log
pdflatex m1-tp-sp-mlp.tex && rm m1-tp-sp-mlp.aux m1-tp-sp-mlp.log  # PNG 保持原图，不重新生成
```

A1、G3 用 [svgkit.py](goldens/svgkit.py)（Helvetica / Menlo 量字宽，rsvg-convert 输出 PNG 和 PDF）；G2 用 PIL 泳道引擎（DejaVu 字体）；MLA、M1 用 TikZ。Mooncake 栈和 Ray 只有 vault 里的 PNG，没有可重新生成的源文件。
