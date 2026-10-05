# Manual evaluation of 27 diagrams

> **Superseded (2026-10-04):** these 27 images were re-scored blind, together with the 27 images of the Oct 4 `gpt-5.6-sol` run, by the reviewer and by Fable 5.1. See [comparisons/2026-10-04-blind-54](../2026-10-04-blind-54/REPORT.md). This report is kept unchanged as the earlier record.

This review compares the skill-assisted, no-skill, and Codex ImageGen outputs for all nine cases. Every PNG was inspected at native resolution. The automated grader results in the earlier run remain separate from this human visual and semantic review.

## Rubric

Each dimension is scored from 1 to 5.

| Dimension | What it measures |
|---|---|
| Fidelity (F) | Whether arrows, labels, shapes, ownership, ordering, and examples match the grounded source behavior |
| Coverage (C) | Whether the diagram includes the relationships and concepts requested by the case prompt |
| Flow | Whether a reader can follow the intended path and hierarchy without reconstructing the layout |
| Legibility (L) | Whether text, spacing, crossings, and aspect ratio remain usable at a normal viewing size |
| Visual encoding (V) | Whether color, grouping, symbols, and polish communicate meaning consistently |

The equal-weight total is out of 25. Because these diagrams explain code and system behavior, a second technical score doubles Fidelity and is out of 30. A high visual score cannot erase a materially wrong connector or tensor shape.

## Scores

| Case | Variant | F | C | Flow | L | V | Total /25 | Technical /30 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| G1 vLLM schedule | Skill | 5 | 5 | 2 | 2 | 3 | 17 | 22 |
| G1 vLLM schedule | No skill | 5 | 5 | 4 | 3 | 4 | 21 | 26 |
| G1 vLLM schedule | ImageGen | 3 | 5 | 5 | 5 | 5 | 23 | 26 |
| G2 verl PPO step | Skill | 5 | 5 | 2 | 2 | 3 | 17 | 22 |
| G2 verl PPO step | No skill | 5 | 5 | 5 | 4 | 4 | 23 | 28 |
| G2 verl PPO step | ImageGen | 2 | 4 | 5 | 5 | 5 | 21 | 23 |
| G3 FFmpeg threads | Skill | 5 | 5 | 3 | 3 | 4 | 20 | 25 |
| G3 FFmpeg threads | No skill | 5 | 5 | 4 | 3 | 4 | 21 | 26 |
| G3 FFmpeg threads | ImageGen | 4 | 4 | 5 | 5 | 5 | 23 | 27 |
| G4 Redis request path | Skill | 5 | 5 | 3 | 2 | 3 | 18 | 23 |
| G4 Redis request path | No skill | 5 | 5 | 5 | 4 | 4 | 23 | 28 |
| G4 Redis request path | ImageGen | 5 | 5 | 5 | 4 | 5 | 24 | 29 |
| M1 Megatron TP/SP MLP | Skill | 5 | 5 | 5 | 5 | 5 | 25 | 30 |
| M1 Megatron TP/SP MLP | No skill | 5 | 5 | 4 | 4 | 4 | 22 | 27 |
| M1 Megatron TP/SP MLP | ImageGen | 4 | 5 | 5 | 5 | 5 | 24 | 28 |
| M2 vLLM mixed-batch attention | Skill | 5 | 5 | 3 | 3 | 4 | 20 | 25 |
| M2 vLLM mixed-batch attention | No skill | 5 | 5 | 5 | 4 | 4 | 23 | 28 |
| M2 vLLM mixed-batch attention | ImageGen | 3 | 5 | 5 | 5 | 5 | 23 | 26 |
| A1 vLLM process architecture | Skill | 5 | 5 | 2 | 2 | 3 | 17 | 22 |
| A1 vLLM process architecture | No skill | 5 | 5 | 5 | 4 | 4 | 23 | 28 |
| A1 vLLM process architecture | ImageGen | 3 | 5 | 5 | 5 | 5 | 23 | 26 |
| A2 verl resource placement | Skill | 5 | 5 | 2 | 2 | 3 | 17 | 22 |
| A2 verl resource placement | No skill | 5 | 5 | 4 | 3 | 4 | 21 | 26 |
| A2 verl resource placement | ImageGen | 2 | 4 | 5 | 5 | 5 | 21 | 23 |
| A3 Megatron parallel groups | Skill | 5 | 5 | 3 | 3 | 4 | 20 | 25 |
| A3 Megatron parallel groups | No skill | 5 | 5 | 5 | 5 | 5 | 25 | 30 |
| A3 Megatron parallel groups | ImageGen | 4 | 5 | 5 | 5 | 5 | 24 | 28 |

## Aggregate comparison

| Variant | Fidelity | Coverage | Flow | Legibility | Visual encoding | Mean /25 | Technical mean /30 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Skill | 5.00 | 5.00 | 2.78 | 2.67 | 3.56 | 19.00 | 24.00 |
| No skill | 5.00 | 5.00 | 4.56 | 3.78 | 4.11 | 22.44 | **27.44** |
| ImageGen | 3.33 | 4.67 | **5.00** | **4.89** | **5.00** | **22.89** | 26.22 |

ImageGen has the highest equal-weight visual score by 0.45 points over no-skill, driven by much stronger flow, legibility, and visual encoding. No-skill has the highest technical score by 1.22 points because it retains source fidelity. Five ImageGen diagrams score 3 or below on Fidelity, so their polish can make errors unusually persuasive.

The technical winner by case is no-skill for G1, G2, M2, A1, A2, and A3; ImageGen for G3 and G4; and the model-architecture skill for M1. G1 is numerically tied between no-skill and ImageGen, but no-skill is preferred because it has no material control-flow error.

## Cross-case style and color consistency

Consistency is evaluated across the nine outputs in each arm. The human scores distinguish a shared visual language from stable color meaning. The numeric hue similarity repeats the repository's existing metric: resize each image to at most 400×400, ignore white, gray, black, and low-value pixels, build a 12-bin hue histogram from the remaining pixels, then average pairwise histogram intersection. It measures palette resemblance only; it does not measure layout, typography, or whether a color means the same thing in two diagrams.

| Variant | Layout and typography coherence /5 | Palette consistency /5 | Mean hue similarity | Semantic color reuse /5 |
|---|---:|---:|---:|---:|
| Skill | 3 | 3 | 0.49 | 3 |
| No skill | 2 | 3 | 0.53 | 2 |
| ImageGen | **5** | **4** | **0.58** | **3** |

**Skill.** The seven Graphviz outputs often reuse the skill's pale fills, role shapes, line treatment, and orange/blue/purple semantic palette. The two model-architecture TikZ figures use a different paper-figure language, and A3 introduces a custom grid palette, so the combined skill arm does not look like one visual family. Its lower all-case hue similarity does not mean the Graphviz template itself is unstable; it mainly reflects combining two distinct skills plus a custom A3 treatment.

**No skill.** The arm mixes Graphviz, hand-drawn Pillow tables, rank cards, swimlanes, and wide pipelines. Several diagrams independently favor blue, which raises hue similarity to 0.53, but typography, edge styles, panel geometry, and color meanings are case-local. It has the weakest visual-system consistency even though some individual diagrams are excellent.

**ImageGen.** All nine outputs share a recognizable infographic language: dark navy headings, rounded white or lightly tinted panels, flat vector icons, restrained shadows, generous spacing, and recurring cyan/blue with orange or purple accents. It is the strongest product-level family. Color remains mostly categorical or decorative: blue, teal, orange, and purple do not preserve one stable technical meaning across all cases, so semantic color reuse scores below its visual palette consistency.

The consistency result therefore has two readings. ImageGen is best when the requirement is a coherent set of presentation graphics. The Graphviz skill has the strongest explicit semantic-color foundation, but that foundation is not shared by the model-architecture skill and is not enforced in every case. No-skill layouts adapt well to each problem, at the cost of a common identity.

## Case findings

| Case | Best practical choice | Main evidence |
|---|---|---|
| G1 | No skill | ImageGen is dramatically easier to read, but its preemption/bypass route terminates at `KVCacheManager` instead of the output path and its success branches are imprecise. |
| G2 | No skill | The no-skill role matrix gives the clearest faithful step sequence. ImageGen sends the next-step path toward checkpoint loading, says the batch is unchanged, and places weight transfer after step 9 even though it occurs within step 9. |
| G3 | ImageGen | It provides the clearest end-to-end pipeline. The DTS feedback arrow, queue slot count, and sync-queue placement need small corrections before publication. |
| G4 | ImageGen | It cleanly distinguishes main-thread parsing/execution from IO-thread reads/writes and preserves the handoffs. Citation text is small, but no material semantic defect was found. |
| M1 | Skill | The TikZ output is both publication quality and exact about forward, backward, weight-gradient paths, and tensor shapes. ImageGen is strong but drops the `2` in `dW2` and leaves flattening implicit. |
| M2 | No skill | ImageGen is much clearer, but the shared `[4,Hq,D]` Q/K/V shape is wrong for grouped-query attention and a slot-mapping arrow enters the projection stage. |
| A1 | No skill | ImageGen communicates the architecture quickly, but worker-return arrows land on the broadcast bus rather than clearly returning to `MultiprocExecutor`, and several module captions are invented. |
| A2 | No skill | ImageGen has the best placement overview, but `teacher_client` and weight-sync connectors are routed to the wrong components. These are central ownership relationships. |
| A3 | No skill | ImageGen is concise and its written group sets are correct, but the embedding rings omit ranks 1, 2, 13, and 14. The no-skill rank-card layout is accurate and highly readable. |

## Cross-arm production cost

For a fair generation comparison, production cost excludes graders. The skill and no-skill values are the recorded agent costs from the Claude eval artifacts. ImageGen uses the recorded Codex agent tokens plus the estimated nine image calls derived below.

| Variant | Nine-image production cost | Cost per image | Technical mean /30 | Technical points per dollar per image |
|---|---:|---:|---:|---:|
| Skill | **$9.63** | **$1.07** | 24.00 | 22.42 |
| No skill | $10.65 | $1.18 | **27.44** | **23.19** |
| ImageGen | $10.94–$12.38 | $1.22–$1.38 | 26.22 | 19.06–21.57 |

The skill arm is cheapest: 9.6% below no-skill and 12–22% below ImageGen, depending on the hidden image quality setting. No-skill is the best technical value because its 10.6% cost premium over the skill arm buys a 3.44-point improvement in technical score. ImageGen costs 2.7–16.2% more than no-skill and produces the most coherent visual family, but its source-fidelity errors keep its technical value below no-skill.

The original Claude evaluation also spent $1.46 judging the skill arm and $1.54 judging the no-skill arm. Including those graders gives $11.09 and $12.19 respectively, but those figures should not be compared directly with ImageGen because this new manual review has no equivalent API-judge charge. The earlier $26.46 archive total additionally includes smoke and superseded runs and is not a production cost for these 18 final images.

The cost-value ratio is descriptive rather than a universal quality metric: it divides the fidelity-weighted score by per-image production cost. It should be read alongside the actual defects and consistency scores, not as a replacement for them.

### ImageGen cost derivation

The nine isolated generation agents used `gpt-6-astra`. Their final session usage records contain 323,802 uncached input tokens, 5,887,872 cached input tokens, and 34,945 output tokens. At the current official GPT-6 Astra rates of $10 per million input tokens and $50 per million output tokens, with cached input charged at the documented 0.1× rate for GPT-5.6 and later, the reasoning-agent estimate is:

`(323,802 × $10 + 5,887,872 × $1 + 34,945 × $50) / 1,000,000 = $10.87`

Sources: [OpenAI model pricing](https://developers.openai.com/api/docs/models) and [prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching).

| Case | Uncached input | Cached input | Output | Estimated agent cost |
|---|---:|---:|---:|---:|
| A1 vLLM process architecture | 45,673 | 941,952 | 4,028 | $1.60 |
| A2 verl resource placement | 40,754 | 763,904 | 4,087 | $1.38 |
| A3 Megatron parallel groups | 23,169 | 461,952 | 3,385 | $0.86 |
| G1 vLLM schedule | 70,528 | 749,440 | 3,914 | $1.65 |
| G2 verl PPO step | 30,609 | 621,184 | 3,994 | $1.13 |
| G3 FFmpeg threads | 25,298 | 586,496 | 3,814 | $1.03 |
| G4 Redis request path | 28,356 | 545,920 | 3,383 | $1.00 |
| M1 Megatron TP/SP MLP | 23,575 | 439,296 | 3,908 | $0.87 |
| M2 vLLM mixed-batch attention | 35,840 | 777,728 | 4,432 | $1.36 |
| **Total** | **323,802** | **5,887,872** | **34,945** | **$10.87** |

The image tool made exactly nine calls with no retries and no image inputs. The saved generation prompts contain 36,347 characters, approximately 9,100 text-input tokens, which add about $0.02 at GPT Image 2's $2.50 per million text-input tokens. The image backend does not expose output-token accounting in these run artifacts, so image output is estimated from OpenAI's published 1536×1024 examples: $0.005 low, $0.041 medium, or $0.165 high per image. Sources: [image generation guide](https://developers.openai.com/api/docs/guides/image-generation) and [API pricing](https://developers.openai.com/api/docs/pricing?tab=suite).

| Image quality assumption | Nine image outputs | Approx. prompt text | Image-tool subtotal | Full nine-case subtotal |
|---|---:|---:|---:|---:|
| Low | $0.05 | $0.02 | $0.07 | $10.94 |
| Medium | $0.37 | $0.02 | $0.39 | $11.26 |
| High | $1.49 | $0.02 | $1.51 | **$12.38** |

The most defensible single estimate is **$12.38** for the complete nine-case ImageGen solution, assuming high-quality image output. The plausible range is **$10.94–$12.38** depending on the hidden image quality setting. This excludes the parent orchestration task and this manual review, and includes the nine isolated reasoning agents plus their nine generated images.
