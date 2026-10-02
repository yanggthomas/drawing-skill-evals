from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .io import load_manifest, png_dimensions, repository_root, sha256

LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
LOCAL_PATH = re.compile(r"/Users/|/private/|generated_images")


def _git_blob(root: Path, path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=root, text=True).strip()


def validate_repository(root: Path | None = None) -> list[str]:
    root = repository_root(root)
    errors: list[str] = []
    catalog = load_manifest(root / "evals/catalog.yaml")
    case_names = {item["name"] for item in catalog["cases"]}
    for case in catalog["cases"]:
        base = root / "evals" / case["name"]
        for required in ("case.yaml", "prompt.md", "answer-key.md", "src/PINNED.txt"):
            if not (base / required).is_file():
                errors.append(f"missing case file: {base / required}")
        for field, relative in (
            ("case_git_blob", "case.yaml"),
            ("prompt_git_blob", "prompt.md"),
            ("pinned_git_blob", "src/PINNED.txt"),
        ):
            target = base / relative
            if target.is_file() and _git_blob(root, target) != case.get(field):
                errors.append(f"case input blob mismatch: {target}")

    run_ids: set[str] = set()
    for manifest_path in sorted((root / "runs").glob("*/run.yaml")):
        run = load_manifest(manifest_path)
        run_ids.add(run["id"])
        base = manifest_path.parent
        if run["id"] != base.name:
            errors.append(f"run id/path mismatch: {manifest_path}")
        for result in run.get("raw", {}).get("final_results", []):
            if not (base / result).is_file():
                errors.append(f"missing raw result: {base / result}")
        for result in run.get("raw", {}).get("historical_attempts", []):
            if not (base / result).is_file():
                errors.append(f"missing historical result: {base / result}")
        review_report = run.get("review", {}).get("report")
        if review_report and not (base / review_report).resolve().is_file():
            errors.append(f"missing run review report: {(base / review_report).resolve()}")
        for comparison in run.get("comparison_refs", []):
            if not (base / comparison).resolve().is_file():
                errors.append(f"missing run comparison: {(base / comparison).resolve()}")
        for case in run.get("cases", []):
            if case["case"] not in case_names:
                errors.append(f"unknown case {case['case']} in {manifest_path}")
            for arm, artifacts in case.get("arms", {}).items():
                arm_root = base / "cases" / case["case"] / "arms" / arm
                for artifact in artifacts:
                    path = arm_root / artifact["path"]
                    if not path.is_file():
                        errors.append(f"missing artifact: {path}")
                        continue
                    if sha256(path) != artifact["sha256"]:
                        errors.append(f"artifact hash mismatch: {path}")
                    if path.suffix.lower() == ".png":
                        try:
                            width, height = png_dimensions(path)
                            if artifact.get("width") != width or artifact.get("height") != height:
                                errors.append(f"PNG dimension mismatch: {path}")
                        except ValueError as exc:
                            errors.append(str(exc))
        if any((base / "cases").glob("*/src")):
            errors.append(f"run duplicates canonical case inputs: {base}")
        migration = base / "migration-map.json"
        if migration.is_file():
            for entry in json.loads(migration.read_text()).get("entries", []):
                if (
                    entry["action"] == "move"
                    and entry.get("sha256")
                    and not entry.get("edited_after_move", False)
                ):
                    target = root / entry["new"]
                    if not target.is_file() or sha256(target) != entry["sha256"]:
                        errors.append(f"migration target mismatch: {target}")
                if entry["action"] == "deduplicate-input":
                    target = root / entry["canonical"]
                    if not target.is_file() or _git_blob(root, target) != entry["git_blob_sha"]:
                        errors.append(f"deduplicated input mismatch: {target}")

    for spec_path in sorted((root / "comparisons").glob("*/comparison.yaml")):
        spec = load_manifest(spec_path)
        base = spec_path.parent
        for key in ("scores", "report", "gallery"):
            if not (base / spec[key]).is_file():
                errors.append(f"missing comparison {key}: {base / spec[key]}")
        for ref in spec.get("source_runs", []):
            path = (base / ref).resolve()
            if not path.is_file():
                errors.append(f"missing comparison source run: {path}")
        scores_path = base / spec["scores"]
        if scores_path.is_file():
            scores = load_manifest(scores_path)
            scored_cases = scores.get("cases", {})
            if set(scored_cases) != {item["id"] for item in catalog["cases"]}:
                errors.append(f"comparison case coverage mismatch: {scores_path}")
            for case_id, case in scored_cases.items():
                if set(case.get("arms", {})) != {"skill", "no_skill", "imagegen"}:
                    errors.append(f"comparison arm coverage mismatch: {scores_path} {case_id}")
                for arm, values in case.get("arms", {}).items():
                    dimensions = [
                        values.get("fidelity"),
                        values.get("coverage"),
                        values.get("flow"),
                        values.get("legibility"),
                        values.get("visual_encoding"),
                    ]
                    if any(value not in range(1, 6) for value in dimensions):
                        errors.append(f"comparison score out of range: {scores_path} {case_id} {arm}")
                        continue
                    if values.get("total_25") != sum(dimensions):
                        errors.append(f"comparison total mismatch: {scores_path} {case_id} {arm}")
                    if values.get("technical_30") != sum(dimensions) + dimensions[0]:
                        errors.append(f"comparison technical total mismatch: {scores_path} {case_id} {arm}")

    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".ai" in path.parts:
            continue
        if path.suffix.lower() in {".md", ".json", ".yaml", ".toml"}:
            text = path.read_text(errors="replace")
            relative = path.relative_to(root)
            is_raw_evidence = "raw" in relative.parts
            is_historical_metrics = "metrics" in relative.parts and path.name == "runs.json"
            if not (is_raw_evidence or is_historical_metrics) and LOCAL_PATH.search(text):
                errors.append(f"machine-local path in archive: {path}")
            if path.suffix.lower() == ".md":
                for raw in LINK.findall(text):
                    target = raw.strip().split("#", 1)[0]
                    if not target or "://" in target or target.startswith("mailto:"):
                        continue
                    if not (path.parent / target).resolve().exists():
                        errors.append(f"broken link: {path} -> {target}")
    return errors
