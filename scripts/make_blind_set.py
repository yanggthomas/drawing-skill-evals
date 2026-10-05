#!/usr/bin/env python3
"""Build the blind 54-image scoring set and its private un-blinding key.

Usage: python3 scripts/make_blind_set.py OUT_DIR

OUT_DIR receives cases/<ID>-<name>/{prompt.md,answer-key.md,src/,images/<token>.png} and
scores.template.json. The key is written to comparisons/2026-10-04-blind-54/blind-key.json and
must stay out of OUT_DIR. PNGs keep only critical chunks, so IDAT (pixel) bytes are unchanged.
"""

import glob
import hashlib
import json
import secrets
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = ROOT / "comparisons" / "2026-10-04-blind-54" / "blind-key.json"
KEEP_CHUNKS = {b"IHDR", b"PLTE", b"tRNS", b"IDAT", b"IEND"}
SIGNATURE = b"\x89PNG\r\n\x1a\n"
OCT01_SKILL = "runs/2026-10-01-skill-v0.1.0"
OCT01_IMAGEGEN = "runs/2026-10-01-codex-imagegen-v1"
OCT04 = "runs/2026-10-04-gpt-5.6-sol-three-arm"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def strip_png(data):
    if not data.startswith(SIGNATURE):
        raise ValueError("not a PNG")
    out, idat, index = [SIGNATURE], [], len(SIGNATURE)
    while index < len(data):
        (length,) = struct.unpack(">I", data[index:index + 4])
        kind = data[index + 4:index + 8]
        chunk = data[index:index + 12 + length]
        if kind in KEEP_CHUNKS:
            out.append(chunk)
        if kind == b"IDAT":
            idat.append(data[index + 8:index + 8 + length])
        index += 12 + length
    return b"".join(out), b"".join(idat)


def oct01_route(case, arm):
    runs = json.loads((ROOT / OCT01_SKILL / "cases" / case / "metrics" / "runs.json").read_text())
    record = next(entry for entry in runs if entry["arm"] == arm)
    used = [skill.split(":")[-1] for skill in record["skills"]] or ["none"]
    return used, record["routes"]


def entries():
    catalog = json.loads((ROOT / "evals" / "catalog.yaml").read_text())["cases"]
    for case in catalog:
        name = case["name"]
        for arm in ("with", "without"):
            used, tools = oct01_route(name, arm)
            yield case, {
                "set": "oct01", "arm": arm, "model": "claude-opus",
                "skills_installed": ["graphviz", "model-architecture"] if arm == "with" else [],
                "skill_used": used, "tools": tools, "image_calls": None,
                "path": glob.glob(f"{ROOT}/{OCT01_SKILL}/cases/{name}/arms/{arm}/*.png"),
            }
        yield case, {
            "set": "oct01", "arm": "imagegen", "model": "gpt-6-astra",
            "skills_installed": ["imagegen"], "skill_used": ["imagegen"], "tools": ["image_gen"],
            "image_calls": 1,
            "path": glob.glob(f"{ROOT}/{OCT01_IMAGEGEN}/cases/{name}/arms/imagegen/*.png"),
        }
        for arm in ("with", "without", "imagegen"):
            audit = json.loads((ROOT / OCT04 / "cases" / name / "arms" / arm / "audit.json").read_text())
            used = [s for s, read in (("graphviz", audit["graphviz_read"]),
                                      ("model-architecture", audit["model_architecture_read"]),
                                      ("imagegen", arm == "imagegen")) if read] or ["none"]
            yield case, {
                "set": "oct04", "arm": arm, "model": audit["model"],
                "skills_installed": audit["expected_skills_visible"], "skill_used": used,
                "tools": sorted({Path(f).suffix.lstrip(".") for f in audit["output_files"]}),
                "image_calls": audit.get("image_generation_calls") if arm == "imagegen" else None,
                "path": [audit["png"]["path"]],
            }


def prompt_body(text):
    if text.startswith("---\n"):
        text = text[text.index("\n---\n", 4) + 5:]
    return text.strip() + "\n"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1]).resolve()
    if KEY.exists():
        sys.exit(f"refusing to overwrite existing key: {KEY}")
    key, template = {}, {"rubric": "results/RUBRIC-FINAL.md", "images": {}}
    by_case = {}
    for case, entry in entries():
        if len(entry["path"]) != 1:
            sys.exit(f"expected one PNG for {case['id']} {entry['set']} {entry['arm']}: {entry['path']}")
        by_case.setdefault(case["id"], (case, []))[1].append(entry)
    for case_id, (case, items) in by_case.items():
        if len(items) != 6:
            sys.exit(f"{case_id}: expected 6 images, found {len(items)}")
        case_dir = out / "cases" / f"{case_id}-{case['name']}"
        evals = ROOT / "evals" / case["name"]
        (case_dir / "images").mkdir(parents=True)
        (case_dir / "prompt.md").write_text(prompt_body((evals / "prompt.md").read_text()))
        shutil.copy2(evals / "answer-key.md", case_dir / "answer-key.md")
        shutil.copytree(evals / "src", case_dir / "src")
        tokens = set()
        for item in items:
            token = secrets.token_hex(4)
            while token in tokens or token in key:
                token = secrets.token_hex(4)
            tokens.add(token)
            original = Path(item.pop("path")[0])
            data = original.read_bytes()
            stripped, idat = strip_png(data)
            (case_dir / "images" / f"{token}.png").write_bytes(stripped)
            key[token] = {
                "case_id": case_id, "case": case["name"], **item,
                "original": str(original.relative_to(ROOT)),
                "original_sha256": sha256(data), "stripped_sha256": sha256(stripped),
                "idat_sha256": sha256(idat),
            }
            template["images"][token] = {
                "case": case_id,
                "scores": {"fidelity": None, "coverage": None, "flow": None,
                           "legibility": None, "visual_encoding": None},
                "total_25": None, "technical_30": None, "defects": [], "rationale": "",
            }
    template["images"] = dict(sorted(template["images"].items(), key=lambda kv: (kv[1]["case"], kv[0])))
    (out / "scores.template.json").write_text(json.dumps(template, indent=2) + "\n")
    KEY.parent.mkdir(parents=True, exist_ok=True)
    KEY.write_text(json.dumps(dict(sorted(key.items())), indent=2) + "\n")
    print(f"wrote {len(key)} images to {out} and key to {KEY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
