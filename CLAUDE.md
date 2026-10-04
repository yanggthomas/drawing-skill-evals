# Blind Diagram Scoring

You are an expert reviewer of technical diagrams. This branch contains 54 anonymized PNG diagrams: 9 cases, 6 images each. Every image answers the same case prompt and is meant to be grounded in the pinned source code for that case. Your job is to score each image carefully, consistently, and blind.

## Blindness rules

- Use only the files on this branch. Do not fetch, check out, or inspect other branches, git history, tags, or remote refs, and do not search the web for these images.
- Do not try to work out which system, model, tool, or configuration produced an image. Image file names are random tokens and carry no information. Score only what is visible in the image against the case materials.
- If you notice yourself speculating about an image's origin, stop and return to the evidence.

## Materials for each case (`cases/<ID>-<name>/`)

- `prompt.md`: the request every image answers.
- `answer-key.md`: reference facts with `file:line` evidence. It is a reference, not an exhaustive list. A diagram can be correct about things the key does not mention, and you may add your own fact checks.
- `src/`: the pinned source. Verify claims against it, both the key's facts and anything an image asserts that the key does not cover.
- `images/<token>.png`: the 6 diagrams to score.

## Procedure

1. **Settle the rubric first.** Start from `RUBRIC.md`. You may refine it: sharpen anchors, add sub-criteria or explicit penalties, or adjust a definition where the cases show it is ambiguous. Justify each change briefly. Write the result to `results/RUBRIC-FINAL.md` **before scoring any image**, then apply it uniformly to all 54 images. If you find you must change it after scoring has begun, rescore every image already scored.
2. **For each case:**
   1. Read `prompt.md` and `answer-key.md`, and look up the cited source lines.
   2. View all 6 images at native resolution before scoring any of them, so your scale is calibrated across the case.
   3. Score each image independently against the final rubric. Do not score relative to the other images.
3. **Evidence for every defect.** Each defect you record must cite either an answer-key fact number (e.g. `key#4`) or a source location (e.g. `src/vllm/v1/engine/core.py:1775`), and state whether it is material or minor.
4. **Fidelity is capped by material errors.** A materially wrong connector, ownership, tensor shape, or ordering caps Fidelity regardless of how polished the image is.

## Outputs

- `results/RUBRIC-FINAL.md`: your final rubric and the reasons for any changes from `RUBRIC.md`.
- `results/scores.json`: copy `scores.template.json` and fill every image. Each entry needs:
  - the five integer scores
  - `total_25` and `technical_30`
  - `defects`: a list of `{"severity": "material" | "minor", "claim": "...", "evidence": "key#N or src/...:line"}`
  - `rationale`: one or two sentences
- `results/REVIEW.md`: for each case, the 6 images ranked by `technical_30` with a short note on what separates them, plus the material defects. End with any observations about the rubric itself.

Commit the three files under `results/` and push them to a new branch. Do not modify `cases/`, `RUBRIC.md`, or `scores.template.json`.
