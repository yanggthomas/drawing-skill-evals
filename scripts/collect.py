"""Collect per-run artifacts and trace facts from a `claude plugin eval --keep-temp` run.

For every run in the results JSON this script:
  - copies the run's workspace `out/` files to <CASE_DIR>/artifacts/<arm>-<n>/
  - records which drawing route the agent took (skills invoked, drawing tools
    used via Bash or written files)
  - flags reads of files outside the vendored `src/` that would leak the skill or
    the answer key into a run (checked post hoc, not as a grader, so it does not
    change either arm's score)
and writes a summary to <CASE_DIR>/artifacts/runs.json.

Reads the kept workspaces as data only: nothing inside them is executed.
"""

import json
import re
import shutil
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


def summarize_run(arm, n, run):
    trace = Path(run["tracePath"])
    info = {"arm": arm, "run": n, "score": run.get("score"), "error": run.get("error"),
            "skills": [], "routes": [], "written": [], "leaks": []}
    if not trace.exists():
        info["error"] = (info["error"] or "") + f" [trace missing: {trace}]"
        return info

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
        print(f"{r['arm']:>7}-{r['run']}  score={r['score']}  skills={r['skills']}  "
              f"routes={r['routes']}  artifacts={r['artifacts']}  leaks={len(r['leaks'])}")
        for leak in r["leaks"]:
            print("          LEAK", leak)


if __name__ == "__main__":
    main()
