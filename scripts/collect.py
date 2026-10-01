"""Collect per-run artifacts and trace facts from a `claude plugin eval --keep-temp` run.

For every run in the results JSON this script:
  - copies the run's workspace `out/` files to <CASE_DIR>/artifacts/<arm>-<n>/
  - records which drawing route the agent took (skills invoked, drawing tools
    used via Bash or written files)
  - reads agent-only time, cost and turns from the trace's final `result` record
    (the harness's per-run figures may include judge calls)
  - keeps a gzipped copy of the trace next to the artifacts
  - flags reads of files outside the vendored `src/` that would leak the skill or
    the answer key into a run (checked post hoc, not as a grader, so it does not
    change either arm's score)
and writes per-run facts to <CASE_DIR>/artifacts/runs.json plus per-arm means.

Reads the kept workspaces as data only: nothing inside them is executed.
"""

import gzip
import json
import re
import shutil
import statistics
from pathlib import Path

RESULTS_JSON = Path("evals/vllm-v1-schedule/results.json")
CASE_DIR = Path("evals/vllm-v1-schedule")
OUT_SUBDIR = "out"  # where the prompt asks the agent to save its diagram

REPO_ROOT = "/home/user/drawing-skill-evals"
# Inside the repo a run may touch only the vendored sources, and in the with-arm
# the plugin's skills. Anything else (answer key, graders, other skills) is a leak.
ALLOWED_ALWAYS = REPO_ROOT + "/evals/vllm-v1-schedule/src"
ALLOWED_WITH_ARM = REPO_ROOT + "/skills/"
LEAK_WORDS = re.compile(r"answer-key|graders/")

def iter_tool_uses(trace_path):
    for line in trace_path.read_text().splitlines():
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(msg, dict) or not isinstance(msg.get("message"), dict):
            continue
        for block in msg["message"].get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                yield block["name"], block.get("input") or {}


# Drawing routes the agent touched (used or just probed, e.g. checking that
# matplotlib is installed), detected by keyword anywhere in a Bash command or written file
# (heredoc bodies included, so `python3 - <<EOF import matplotlib` counts).
ROUTES = {
    "graphviz": r"\b(dot|neato|fdp|sfdp|circo|twopi)\b\s+-T|\.dot\b|\bgraphviz\b",
    "mermaid": r"\bmmdc\b|\.mmd\b|mermaid",
    "tikz/latex": r"\b(pdflatex|xelatex|lualatex|latexmk)\b|tikzpicture",
    "matplotlib": r"\bmatplotlib\b",
    "pillow": r"\bfrom PIL\b|\bimport PIL\b",
    "svg": r"<svg\b|\.svg\b",
    "image-model/network": r"\b(curl|wget|diffusers|openai|stability|replicate|dall-?e|imagen|gpt-image)\b",
}


def routes_in(text):
    return [name for name, pat in ROUTES.items() if re.search(pat, text, re.I)]


def is_leak(arm, text):
    if LEAK_WORDS.search(text):
        return True
    for path in re.findall(re.escape(REPO_ROOT) + r"[^\s\"']*", text):
        if path.startswith(ALLOWED_ALWAYS):
            continue
        if arm == "with" and path.startswith(ALLOWED_WITH_ARM):
            continue
        return True
    return False


def agent_result(trace_path):
    """The agent session's own `result` record: excludes judge calls and harness overhead."""
    result = None
    for line in trace_path.read_text().splitlines():
        if '"type": "result"' in line or '"type":"result"' in line:
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(msg, dict) and msg.get("type") == "result":
                result = msg
    if result is None:
        return {}
    return {
        "agent_seconds": round(result.get("duration_ms", 0) / 1000, 1),
        "agent_api_seconds": round(result.get("duration_api_ms", 0) / 1000, 1),
        "agent_cost_usd": round(result.get("total_cost_usd", 0), 4),
        "agent_turns": result.get("num_turns"),
    }


def summarize_run(arm, n, run):
    trace = Path(run["tracePath"])
    info = {"arm": arm, "run": n, "score": run.get("score"), "error": run.get("error"),
            "judge_cost_usd": round(run.get("judgeCostUsd") or 0, 4),
            "skills": [], "routes": [], "written": [], "leaks": []}
    if not trace.exists():
        info["error"] = (info["error"] or "") + f" [trace missing: {trace}]"
        return info
    info.update(agent_result(trace))

    for name, inp in iter_tool_uses(trace):
        if name == "Skill":
            info["skills"].append(inp.get("skill"))
        elif name in ("Bash", "Write"):
            if name == "Write":
                info["written"].append(inp.get("file_path"))
            body = inp.get("command", "") + inp.get("file_path", "") + inp.get("content", "")
            info["routes"] += [r for r in routes_in(body) if r not in info["routes"]]
        text = json.dumps(inp)
        if is_leak(arm, text):
            info["leaks"].append(f"{name}: {text[:200]}")

    # Workspace layout: <tmp>/out/trace.jsonl and <tmp>/home/cwd/<agent files>.
    out_dir = trace.parent.parent / "home" / "cwd" / OUT_SUBDIR
    dest = CASE_DIR / "artifacts" / f"{arm}-{n}"
    if out_dir.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        for f in out_dir.iterdir():
            if f.is_file() and not f.is_symlink():
                shutil.copyfile(f, dest / f.name)
        with trace.open("rb") as src, gzip.open(dest / "trace.jsonl.gz", "wb") as dst:
            shutil.copyfileobj(src, dst)
        info["artifacts"] = sorted(p.name for p in dest.iterdir())
    else:
        info["artifacts"] = []
    return info


def main():
    results = json.loads(RESULTS_JSON.read_text())
    runs = []
    for case in results["cases"]:
        for arm, arm_runs in case["arms"].items():
            for n, run in enumerate(arm_runs, start=1):
                runs.append(summarize_run(arm, n, run))

    (CASE_DIR / "artifacts").mkdir(parents=True, exist_ok=True)
    (CASE_DIR / "artifacts" / "runs.json").write_text(json.dumps(runs, indent=2))
    for r in runs:
        print(f"{r['arm']:>7}-{r['run']}  score={r['score']}  "
              f"agent={r.get('agent_seconds')}s ${r.get('agent_cost_usd')} turns={r.get('agent_turns')}  "
              f"skills={r['skills']}  routes={r['routes']}  leaks={len(r['leaks'])}")
        for leak in r["leaks"]:
            print("          LEAK", leak)

    # Per-arm agent-only statistics (judge cost reported separately).
    summary = {}
    for arm in sorted({r["arm"] for r in runs}):
        arm_runs = [r for r in runs if r["arm"] == arm and "agent_seconds" in r]
        summary[arm] = {"n": len(arm_runs)}
        for key in ("agent_seconds", "agent_api_seconds", "agent_cost_usd", "agent_turns", "judge_cost_usd"):
            vals = [r[key] for r in arm_runs if r.get(key) is not None]
            if vals:
                summary[arm][key] = {
                    "mean": round(statistics.mean(vals), 3),
                    "median": round(statistics.median(vals), 3),
                    "sd": round(statistics.stdev(vals), 3) if len(vals) > 1 else None,
                    "min": min(vals), "max": max(vals),
                }
    (CASE_DIR / "artifacts" / "summary.json").write_text(json.dumps(summary, indent=2))
    print()
    for arm, s in summary.items():
        line = [f"{arm:>7} n={s['n']}"]
        for key, label in (("agent_seconds", "time s"), ("agent_cost_usd", "cost $"),
                           ("agent_turns", "turns"), ("judge_cost_usd", "judge $")):
            if key in s:
                st = s[key]
                line.append(f"{label}: mean {st['mean']} median {st['median']} sd {st['sd']}")
        print("  |  ".join(line))


if __name__ == "__main__":
    main()
