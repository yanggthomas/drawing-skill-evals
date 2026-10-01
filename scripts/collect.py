"""Collect per-run artifacts and trace facts from a `claude plugin eval --keep-temp` run.

For every case and run in the results JSON this script:
  - copies the run's workspace `out/` files to <case dir>/artifacts/<arm>-<n>/
  - records which drawing route the agent took (skills invoked, drawing tools
    used via Bash or written files)
  - reads agent-only time, cost and turns from the trace's final `result` record
    (the harness's per-run figures may include judge calls)
  - keeps a gzipped copy of the trace next to the artifacts
  - flags reads of files outside the vendored `src/` that would leak the skill or
    the answer key into a run (checked post hoc, not as a grader, so it does not
    change either arm's score)
and writes per-run facts to <case dir>/artifacts/runs.json plus per-arm stats to
<case dir>/artifacts/summary.json, then prints one table for the whole suite.

Reads the kept workspaces as data only: nothing inside them is executed.
"""

import gzip
import json
import re
import shutil
import statistics
from pathlib import Path

RESULTS_JSON = Path("evals/results.json")  # the --json file of the run to collect
OUT_SUBDIR = "out"  # where the prompt asks the agent to save its diagram

REPO_ROOT = "/home/user/drawing-skill-evals"
# Inside the repo a run may touch only its case's vendored src/, and in the
# with-arm the plugin's skills. Anything else (answer key, graders) is a leak.
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


def is_leak(arm, text, allowed_src):
    if LEAK_WORDS.search(text):
        return True
    for path in re.findall(re.escape(REPO_ROOT) + r"[^\s\"']*", text):
        if path.startswith(allowed_src):
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


def summarize_run(case_dir, arm, n, run):
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
        if is_leak(arm, text, f"{REPO_ROOT}/{case_dir}/src"):
            info["leaks"].append(f"{name}: {text[:200]}")

    # Workspace layout: <tmp>/out/trace.jsonl and <tmp>/home/cwd/<agent files>.
    out_dir = trace.parent.parent / "home" / "cwd" / OUT_SUBDIR
    dest = case_dir / "artifacts" / f"{arm}-{n}"
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


def arm_stats(runs):
    """Per-arm agent-only statistics (judge cost reported separately)."""
    summary = {}
    for arm in sorted({r["arm"] for r in runs}):
        arm_runs = [r for r in runs if r["arm"] == arm]
        summary[arm] = {"n": len(arm_runs)}
        for key in ("score", "agent_seconds", "agent_api_seconds", "agent_cost_usd", "agent_turns",
                    "judge_cost_usd"):
            vals = [r[key] for r in arm_runs if r.get(key) is not None]
            if vals:
                summary[arm][key] = {
                    "mean": round(statistics.mean(vals), 3),
                    "median": round(statistics.median(vals), 3),
                    "sd": round(statistics.stdev(vals), 3) if len(vals) > 1 else None,
                    "min": min(vals), "max": max(vals),
                }
    return summary


def main():
    results = json.loads(RESULTS_JSON.read_text())
    print(f"{'case':<26} {'arm':<8} {'score':>5} {'agent s':>8} {'agent $':>8} {'turns':>5} "
          f"{'judge $':>7}  skills / routes / leaks")
    for case in results["cases"]:
        case_dir = Path(case["dir"])
        runs = [summarize_run(case_dir, arm, n, run)
                for arm, arm_runs in case["arms"].items()
                for n, run in enumerate(arm_runs, start=1)]
        (case_dir / "artifacts").mkdir(parents=True, exist_ok=True)
        (case_dir / "artifacts" / "runs.json").write_text(json.dumps(runs, indent=2))
        (case_dir / "artifacts" / "summary.json").write_text(json.dumps(arm_stats(runs), indent=2))
        for r in runs:
            score = f"{r['score']:.2f}" if r["score"] is not None else "-"
            print(f"{case['name']:<26} {r['arm']}-{r['run']:<6} {score:>5} "
                  f"{r.get('agent_seconds', '-'):>8} {r.get('agent_cost_usd', '-'):>8} "
                  f"{r.get('agent_turns', '-'):>5} {r['judge_cost_usd']:>7}  "
                  f"{r['skills']} / {r['routes']} / {len(r['leaks'])}")
            for leak in r["leaks"]:
                print("    LEAK", leak)
            if r["error"]:
                print("    ERROR", r["error"])

if __name__ == "__main__":
    main()
