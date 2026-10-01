"""Build REPORT.md from eval results and the per-case artifacts written by collect.py.

Per case it records: the question, the pinned source, scores and every grader's
verdict per arm, agent-only time / cost / turns (judge cost separately), the
drawing route, skill routing, leak check, the final images of both arms, and the
hand-written observations in <case dir>/notes.md if present.
"""

import colorsys
import itertools
import json
import re
import statistics
from pathlib import Path

from PIL import Image

# Results files to include, in report order (one entry per `claude plugin eval --json` run).
RESULTS_FILES = [
    Path("evals/vllm-v1-schedule/results.json"),  # round 1: G1
    Path("evals/results.json"),                   # round 2: G2 G3 G4 M1 M2
    Path("evals/results-arch.json"),              # round 3: A1 A2 A3 (architecture)
]
REPORT = Path("REPORT.md")
CASE_IDS = {
    "vllm-v1-schedule": "G1",
    "verl-ppo-step": "G2",
    "ffmpeg-transcode-threads": "G3",
    "redis-request-path": "G4",
    "megatron-tp-sp-mlp": "M1",
    "vllm-v1-mixed-batch-attn": "M2",
    "vllm-v1-process-arch": "A1",
    "verl-resource-placement": "A2",
    "megatron-parallel-groups": "A3",
}
CASE_ORDER = list(CASE_IDS)
# What kind of diagram each prompt asks for, and whether that is inside the routed skill's design scope.
# graphviz is designed for architecture / topology; model-architecture for model internals (tensors, layers).
CASE_KIND = {
    "vllm-v1-schedule": "流程（单步算法）",
    "verl-ppo-step": "流程（训练步骤顺序）",
    "ffmpeg-transcode-threads": "混合（线程拓扑 + 背压/同步）",
    "redis-request-path": "时序（跨线程请求生命周期）",
    "megatron-tp-sp-mlp": "模型内部（张量形状 + 通信）",
    "vllm-v1-mixed-batch-attn": "模型内部（逐 token 元数据）",
    "vllm-v1-process-arch": "架构（进程与组件）",
    "verl-resource-placement": "架构（资源池与放置）",
    "megatron-parallel-groups": "架构（rank 与并行组拓扑）",
}
GROUPS = {  # consistency groups: label -> case ids
    "流程/时序/混合（graphviz 设计范围外）": ["G1", "G2", "G3", "G4"],
    "模型内部（model-architecture 范围内）": ["M1", "M2"],
    "架构（graphviz 范围内）": ["A1", "A2", "A3"],
}
SCORED_GRADERS = ["render", "correctness", "readability"]
INDICATORS = ["skill-fired", "skill-misrouted"]
ARM_LABEL = {"with": "带 skill", "without": "不带 skill"}
HUE_BINS = 12            # colour-style fingerprint: hue histogram of saturated pixels
MIN_SAT, MIN_VAL = 0.05, 0.25  # 0.05 keeps pale fills (light blue, lavender); text and grey stay out
REVIEW_KEYS = {"content": "信息完整", "layout": "版式清晰", "color": "配色"}  # Claude's 1-5 review per image


def fmt(v, digits=2, prefix=""):
    if v is None:
        return "–"
    if isinstance(v, float):
        return f"{prefix}{v:.{digits}f}"
    return f"{prefix}{v}"


def verdict(g):
    if g is None:
        return "–"
    mark = "✅" if g["passed"] else "❌"
    votes = g.get("judgeVotes")
    if votes:
        mark += " " + "".join("✓" if v else "✗" for v in votes)
    return mark


def prompt_body(case_dir):
    text = (case_dir / "prompt.md").read_text()
    return text.split("---", 2)[2].strip()


def pinned(case_dir):
    p = (case_dir / "src" / "PINNED.txt").read_text()
    repo = re.search(r"^repo:\s+(\S+)", p, re.M).group(1)
    commit = re.search(r"^commit:\s+(\S+)", p, re.M).group(1)
    ref = re.search(r"^ref:\s+(.+)$", p, re.M)
    ref = ref.group(1).strip() if ref else "main"
    files = re.findall(r"^  (\S+)", p, re.M)
    return repo, ref, commit, files


def answer_key_titles(case_dir):
    return re.findall(r"^\d+\. \*\*(.+?)\*\*", (case_dir / "answer-key.md").read_text(), re.M)


def pass_rule(case_dir):
    m = re.search(r"PASS if at least (\d+) of the (\d+) facts", (case_dir / "graders/correctness.md").read_text())
    return f"{m.group(1)}/{m.group(2)}" if m else "–"


def load_cases():
    cases = []
    for rf in RESULTS_FILES:
        if not rf.exists():
            continue
        results = json.loads(rf.read_text())
        for case in results["cases"]:
            case_dir = Path(case["dir"])
            runs_file = case_dir / "artifacts" / "runs.json"
            facts = json.loads(runs_file.read_text()) if runs_file.exists() else []
            arms = {}
            for arm, arm_runs in case["arms"].items():
                run = arm_runs[0]  # one run per arm in this study
                fact = next((f for f in facts if f["arm"] == arm and f["run"] == 1), {})
                arms[arm] = {"run": run, "fact": fact,
                             "graders": {g["name"]: g for g in run.get("graders", [])}}
            cases.append({"name": case["name"], "dir": case_dir, "arms": arms,
                          "report_url": results.get("reportUrl")})
    return sorted(cases, key=lambda c: CASE_ORDER.index(c["name"]) if c["name"] in CASE_ORDER else 99)


def final_route(case_dir, arm, fact):
    """The tool that produced the final PNG, read from the kept source files; probes don't count."""
    d = case_dir / "artifacts" / f"{arm}-1"
    names = [p.name for p in d.iterdir()] if d.is_dir() else []
    if any(n.endswith(".tex") for n in names):
        return "TikZ"
    if any(n.endswith(".dot") for n in names):
        return "Graphviz"
    if any(n.endswith(".mmd") for n in names):
        return "Mermaid"
    for n in names:
        if n.endswith(".py"):
            src = (d / n).read_text(errors="ignore")
            if re.search(r"^\s*(from|import) matplotlib", src, re.M):
                return "matplotlib"
            if re.search(r"^\s*from PIL", src, re.M):
                return "Pillow (逐个画形状)"
            return "Python"
    # Source kept outside out/: fall back to the routes seen in the trace, minus mere probes.
    routes = [r for r in fact.get("routes") or [] if r not in ("matplotlib", "pillow")]
    return {"graphviz": "Graphviz", "mermaid": "Mermaid", "tikz/latex": "TikZ", "svg": "SVG"}.get(
        routes[0], routes[0]) if routes else "–"


def image_for(case_dir, arm):
    d = case_dir / "artifacts" / f"{arm}-1"
    pngs = sorted(d.glob("*.png")) if d.is_dir() else []
    return pngs[0] if pngs else None


def summary_table(cases):
    lines = [
        "| Case | 题型 | 得分 带 / 不带 | Δ | agent 耗时 带 / 不带 (s) | agent 花费 带 / 不带 ($) | 轮数 带 / 不带 | skill 路由 | 画图路线 带 / 不带 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    tot = {"with": [0.0, 0.0, 0.0], "without": [0.0, 0.0, 0.0]}  # seconds, agent $, judge $
    for c in cases:
        w, o = c["arms"].get("with"), c["arms"].get("without")
        sw, so = w["run"]["score"], o["run"]["score"]
        fw, fo = w["fact"], o["fact"]
        for arm, f in (("with", fw), ("without", fo)):
            tot[arm][0] += f.get("agent_seconds") or 0
            tot[arm][1] += f.get("agent_cost_usd") or 0
            tot[arm][2] += f.get("judge_cost_usd") or 0
        fired = w["graders"].get("skill-fired")
        misrouted = w["graders"].get("skill-misrouted")
        routing = ("✅" if fired and fired["passed"] else "❌ 未触发") + (
            "" if not misrouted or misrouted["passed"] else " ⚠ 误用")
        lines.append(
            f"| {CASE_IDS.get(c['name'], '')} `{c['name']}` | {CASE_KIND.get(c['name'], '')} | {sw:.2f} / {so:.2f} | {sw - so:+.2f} | "
            f"{fmt(fw.get('agent_seconds'), 0)} / {fmt(fo.get('agent_seconds'), 0)} | "
            f"{fmt(fw.get('agent_cost_usd'))} / {fmt(fo.get('agent_cost_usd'))} | "
            f"{fmt(fw.get('agent_turns'))} / {fmt(fo.get('agent_turns'))} | {routing} | "
            f"{final_route(c['dir'], 'with', fw)} / {final_route(c['dir'], 'without', fo)} |")
    n = len(cases)
    mean_w = sum(c["arms"]["with"]["run"]["score"] for c in cases) / n
    mean_o = sum(c["arms"]["without"]["run"]["score"] for c in cases) / n
    lines.append(
        f"| **合计 / 平均** | | **{mean_w:.2f} / {mean_o:.2f}** | **{mean_w - mean_o:+.2f}** | "
        f"**{tot['with'][0]:.0f} / {tot['without'][0]:.0f}** | **{tot['with'][1]:.2f} / {tot['without'][1]:.2f}** | | | |")
    judge = tot["with"][2] + tot["without"][2]
    agent = tot["with"][1] + tot["without"][1]
    return "\n".join(lines), agent, judge


def grader_table(c):
    lines = ["| 评分器 | 带 skill | 不带 skill | 说明 |", "|---|---|---|---|"]
    notes = {"render": "生成了 PNG", "correctness": f"答案要点至少 {pass_rule(c['dir'])} 画对且无矛盾",
             "readability": "可读性（文字、重叠、方向、连线、视觉语法、孤立节点）",
             "skill-fired": "调用了应调用的 skill（只作指示）",
             "skill-misrouted": "没有调用另一个 skill（只作指示）"}
    for name in SCORED_GRADERS + INDICATORS:
        lines.append(f"| {name} | {verdict(c['arms']['with']['graders'].get(name))} | "
                     f"{verdict(c['arms']['without']['graders'].get(name)) if name in SCORED_GRADERS else '–'} | {notes[name]} |")
    return "\n".join(lines)


def run_table(c):
    lines = ["| | 带 skill | 不带 skill |", "|---|---|---|"]
    rows = [("得分", lambda a: fmt(a["run"]["score"])),
            ("agent 耗时 (s)", lambda a: fmt(a["fact"].get("agent_seconds"), 1)),
            ("agent API 耗时 (s)", lambda a: fmt(a["fact"].get("agent_api_seconds"), 1)),
            ("agent 花费 ($)", lambda a: fmt(a["fact"].get("agent_cost_usd"), 3)),
            ("评委花费 ($)", lambda a: fmt(a["fact"].get("judge_cost_usd"), 3)),
            ("轮数", lambda a: fmt(a["fact"].get("agent_turns"))),
            ("调用的 skill", lambda a: ", ".join(a["fact"].get("skills") or []) or "无"),
            ("最终画图路线", None),
            ("碰过的绘图工具（含只探测过的）", lambda a: ", ".join(a["fact"].get("routes") or []) or "–"),
            ("越界读文件", lambda a: str(len(a["fact"].get("leaks") or [])) if a["fact"] else "–"),
            ("错误", lambda a: a["run"].get("error") or "无")]
    for label, f in rows:
        if f is None:  # final route needs the case dir
            cells = [final_route(c["dir"], arm, c["arms"][arm]["fact"]) for arm in ("with", "without")]
        else:
            cells = [f(c["arms"][arm]) for arm in ("with", "without")]
        lines.append(f"| {label} | {cells[0]} | {cells[1]} |")
    return "\n".join(lines)


def case_section(c):
    d = c["dir"]
    cid = CASE_IDS.get(c["name"], "")
    repo, ref, commit, files = pinned(d)
    titles = answer_key_titles(d)
    out = [f"## {cid} · `{c['name']}`", "", f"**题型：** {CASE_KIND.get(c['name'], '–')}  "]
    out += [f"**代码库：** {repo} @ `{commit[:10]}`（{ref}）  ",
            f"**复制进来的源码：** {', '.join(f'`{f}`' for f in files)}  ",
            f"**答案要点：** [{d}/answer-key.md]({d}/answer-key.md)（{len(titles)} 条，通过线 {pass_rule(d)}）", ""]
    out += ["**Prompt：**", "", "> " + prompt_body(d), ""]
    out += ["**答案要点标题：** " + " · ".join(f"{i}. {t}" for i, t in enumerate(titles, 1)), ""]
    out += ["### 评分", "", grader_table(c), "", "### 运行数据（agent 部分不含评委）", "", run_table(c), ""]
    out += content_detail(c)
    out += ["### 最终的图", ""]
    for arm in ("with", "without"):
        img = image_for(d, arm)
        out += [f"**{ARM_LABEL[arm]}**", ""]
        out += [f"![{c['name']} {ARM_LABEL[arm]}]({img})" if img else "_没有生成 PNG_", ""]
    notes = d / "notes.md"
    if notes.exists():
        out += ["### 观察", "", notes.read_text().strip(), ""]
    return "\n".join(out)


def hue_histogram(png):
    """Normalized hue histogram of saturated pixels; white/grey/black background is ignored."""
    img = Image.open(png).convert("RGB")
    img.thumbnail((400, 400))
    hist = [0.0] * HUE_BINS
    pixels = img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata()
    for r, g, b in pixels:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if s >= MIN_SAT and v >= MIN_VAL:
            hist[int(h * HUE_BINS) % HUE_BINS] += 1
    total = sum(hist)
    return [x / total for x in hist] if total else None


def style_similarity(pngs):
    """Mean pairwise histogram intersection (0..1) between images' hue histograms."""
    hists = [h for h in (hue_histogram(p) for p in pngs) if h]
    pairs = list(itertools.combinations(hists, 2))
    if not pairs:
        return None
    return statistics.mean(sum(min(a, b) for a, b in zip(x, y)) for x, y in pairs)


def spread(vals):
    if len(vals) < 2:
        return None
    return statistics.pstdev(vals)


def clip01(x):
    return None if x is None else max(0.0, min(1.0, x))


def load_review(case_dir):
    f = case_dir / "review.json"
    return json.loads(f.read_text()) if f.exists() else {}


def consistency_section(cases):
    lines = [
        "## 一致性 / 可预测性", "",
        "每个 case 每组只有 1 次运行，所以这里比较的是**同一题型的 case 之间**的波动（每类 2–4 个 case，样本很少，只作参考）。",
        "", "指标定义：",
        "- **质量一致性** = 1 − 2·σ(得分)。得分在 0–1 之间，σ 最大 0.5，所以 1 = 各 case 得分完全一样，0 = 最分散。",
        "- **耗时 / 花费可预测性** = 1 − CV，CV = σ / 均值（agent 部分，不含评委），截到 0–1。",
        "- **风格一致性** = 各图色相直方图两两交集的均值；只统计有颜色的像素，含浅色填充，忽略白、灰、黑。1 = 配色分布完全相同。",
        "- **看图评分一致性** = 1 − σ(看图均分)/2。看图分是 1–5 分，σ 最大 2，所以范围 0–1。",
        "- σ 用总体标准差。", "",
        "| 类别 | 组 | n | 得分 均值 [范围] | 质量一致性 | correctness 通过率 | readability 通过率 "
        "| 耗时 均值 s (可预测性) | 花费 均值 $ (可预测性) | 风格一致性 | 看图均分 (一致性) | skill 正确触发 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for label, ids in GROUPS.items():
        group = [c for c in cases if CASE_IDS.get(c["name"]) in ids]
        if not group:
            continue
        for arm in ("with", "without"):
            scores = [c["arms"][arm]["run"]["score"] for c in group]
            secs = [c["arms"][arm]["fact"].get("agent_seconds") for c in group]
            cost = [c["arms"][arm]["fact"].get("agent_cost_usd") for c in group]
            secs = [x for x in secs if x is not None]
            cost = [x for x in cost if x is not None]
            corr = [c["arms"][arm]["graders"].get("correctness", {}).get("passed") for c in group]
            read = [c["arms"][arm]["graders"].get("readability", {}).get("passed") for c in group]
            imgs = [p for p in (image_for(c["dir"], arm) for c in group) if p]
            reviews = []
            for c in group:
                r = load_review(c["dir"]).get(arm)
                if r:
                    reviews.append(statistics.mean(r[k] for k in REVIEW_KEYS))
            sd = spread(scores)
            q = "–" if sd is None else f"{clip01(1 - 2 * sd):.2f}"
            def pred(vals):
                if len(vals) < 2 or not statistics.mean(vals):
                    return "–"
                return f"{clip01(1 - statistics.pstdev(vals) / statistics.mean(vals)):.2f}"
            style = style_similarity(imgs)
            rv = "–"
            if reviews:
                rsd = spread(reviews)
                rv = f"{statistics.mean(reviews):.1f} ({'–' if rsd is None else f'{clip01(1 - rsd / 2):.2f}'})"
            fired = "–"
            if arm == "with":
                ok = [c["arms"]["with"]["graders"].get("skill-fired", {}).get("passed") for c in group]
                bad = [not c["arms"]["with"]["graders"].get("skill-misrouted", {}).get("passed", True) for c in group]
                fired = f"{sum(bool(x) for x in ok)}/{len(group)}" + (f"，误用 {sum(bad)}" if any(bad) else "")
            lines.append(
                f"| {label if arm == 'with' else ''} | {ARM_LABEL[arm]} | {len(group)} | "
                f"{statistics.mean(scores):.2f} [{min(scores):.2f}–{max(scores):.2f}] | {q} | "
                f"{sum(bool(x) for x in corr)}/{len(group)} | {sum(bool(x) for x in read)}/{len(group)} | "
                f"{statistics.mean(secs):.0f} ({pred(secs)}) | {statistics.mean(cost):.2f} ({pred(cost)}) | "
                f"{'–' if style is None else f'{style:.2f}'} | {rv} | {fired} |")
    return "\n".join(lines)


def load_content_review(case_dir):
    f = case_dir / "content-review.json"
    return json.loads(f.read_text()) if f.exists() else None


def content_table(cases):
    rows = [(c, load_content_review(c["dir"])) for c in cases]
    rows = [(c, r) for c, r in rows if r]
    if not rows:
        return ""
    lines = ["## 内容可读性（Claude 逐子问题检查）", "",
             "只看内容：把每个 prompt 明确问的子问题列出来，看读者能不能从图里直接读到答案。"
             "每个子问题 2 = 一眼可读，1 = 在图里但要在小字或代码里找，0 = 读不出或画错。"
             "另给一个 1–5 的整体分：读者能不能把题目要的那条主线拼起来。这是模型的判断，不是人工打分。", "",
             "| Case | 题型 | 子问题得分 带 / 不带 | 内容可读性 (1–5) 带 / 不带 |", "|---|---|---|---|"]
    tw = to = tmax = 0
    sw, so = [], []
    for c, r in rows:
        mx = 2 * len(r["questions"])
        tw += sum(r["with"]); to += sum(r["without"]); tmax += mx
        sw.append(r["with_score"]); so.append(r["without_score"])
        lines.append(f"| {CASE_IDS.get(c['name'], '')} | {CASE_KIND.get(c['name'], '')} | "
                     f"{sum(r['with'])}/{mx} / {sum(r['without'])}/{mx} | {r['with_score']} / {r['without_score']} |")
    lines.append(f"| **合计 / 平均** | | **{tw}/{tmax} / {to}/{tmax}** | "
                 f"**{statistics.mean(sw):.1f} / {statistics.mean(so):.1f}** |")
    return "\n".join(lines)


def content_detail(c):
    r = load_content_review(c["dir"])
    if not r:
        return []
    out = ["### 内容可读性", "", "| 子问题 | 带 skill | 不带 skill |", "|---|---|---|"]
    mark = {2: "2 一眼可读", 1: "1 要找", 0: "0 读不出"}
    for q, a, b in zip(r["questions"], r["with"], r["without"]):
        out.append(f"| {q} | {mark[a]} | {mark[b]} |")
    out += [f"| **整体 (1–5)** | **{r['with_score']}** | **{r['without_score']}** |", "", r["note"], ""]
    return out


def review_table(cases):
    if not any(load_review(c["dir"]) for c in cases):
        return ""
    head = " | ".join(f"{v} 带/不带" for v in REVIEW_KEYS.values())
    lines = ["## Claude 看图评分（1–5）", "",
             "我逐张检查了所有最终 PNG，按同一标准打分。这是模型打的分，**不是人工美观打分**（人工打分见 PLAN 第 9 步）。标准：",
             "- **信息完整**：题目要求的机制是否都画出来、是否与代码一致；",
             "- **版式清晰**：阅读方向、交叉线、文字大小、留白、分区；",
             "- **配色**：色板克制、颜色有含义、对比度、整体协调。", "",
             f"| Case | {head} | 均分 带/不带 |", "|---|" + "---|" * (len(REVIEW_KEYS) + 1)]
    for c in cases:
        r = load_review(c["dir"])
        if not r:
            continue
        cells = [f"{r['with'][k]} / {r['without'][k]}" for k in REVIEW_KEYS]
        mw = statistics.mean(r["with"][k] for k in REVIEW_KEYS)
        mo = statistics.mean(r["without"][k] for k in REVIEW_KEYS)
        lines.append(f"| {CASE_IDS.get(c['name'], '')} | " + " | ".join(cells) + f" | {mw:.1f} / {mo:.1f} |")
    return "\n".join(lines)


def main():
    cases = load_cases()
    table, agent_cost, judge_cost = summary_table(cases)
    head = [
        "# 绘图 skill A/B 评测报告", "",
        "评测对象：本仓库的 `drawing-skills` 插件（`graphviz`、`model-architecture` 两个 skill）。"
        "每个 case 跑两组：带插件（带 skill）和不带插件（不带 skill），**每组 1 次**；agent 和评委都是 Opus。"
        "prompt 不指定画图工具，只要求输出一张 PNG。分数 = render、correctness、readability 三个评分器的通过比例；"
        "skill 是否触发只作指示，不计分。美观和配色由人工另行打分（见 PLAN 第 9 步）。", "",
        "> 每组只有 1 个样本，Δ 和耗时差都是单次观测，不是稳定结论。", "",
        "**读结果前先看题型。** graphviz skill 是为**架构图**设计的（SKILL.md：“topology-first graphs”，并明确“Not for UML sequence / activity”）。"
        "第 1、2 轮的 G1–G4 问的是单步算法、训练步骤顺序、跨线程请求生命周期，属于流程图 / 时序图，**在 graphviz skill 的设计范围之外**；"
        "M1、M2 在 model-architecture skill 的范围内。第 3 轮的 A1–A3 是只问组成与连接的架构题，用来测 graphviz skill 的主场。", "",
        "## 汇总", "", table, "",
        f"agent 花费合计 ${agent_cost:.2f}，评委花费合计 ${judge_cost:.2f}，总计 ${agent_cost + judge_cost:.2f}。", "",
    ]
    head += [consistency_section(cases), ""]
    ct = content_table(cases)
    if ct:
        head += [ct, ""]
    rt = review_table(cases)
    if rt:
        head += [rt, ""]
    overall = Path("evals/notes.md")
    if overall.exists():
        head += ["## 总体观察", "", overall.read_text().strip(), ""]
    pending = [n for n in CASE_ORDER if n not in {c["name"] for c in cases} and Path("evals", n, "prompt.md").exists()]
    if pending:
        head += ["## 待跑的 case", "",
                 "以下 case 已写好（源码、答案要点、评分器齐全），还没有运行结果：", ""]
        head += [f"- {CASE_IDS[n]} `{n}`：{CASE_KIND[n]}（[答案要点](evals/{n}/answer-key.md)）" for n in pending]
        head += [""]
    improvements = Path("SKILL-IMPROVEMENTS.md")
    if improvements.exists():
        head += ["## skill 强化方案", "", f"见 [{improvements}]({improvements})。", ""]
    body = [case_section(c) for c in cases]
    REPORT.write_text("\n".join(head) + "\n" + "\n\n".join(body) + "\n")
    print(f"wrote {REPORT} with {len(cases)} cases")


if __name__ == "__main__":
    main()
