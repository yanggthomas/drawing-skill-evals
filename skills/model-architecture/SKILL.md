---
name: model-architecture
description: Create, reconstruct, edit, compile, and visually verify publication-style TikZ figures for ML and LLM model internals. Use for tensor or vector flows, neural-network layers, attention and transformer mechanisms, operator-level computation graphs, residual paths, mathematical labels, and paper-figure reconstruction. Do not use for software/system topology or mind maps (Graphviz), UML diagrams (Mermaid), data plots, or decorative raster illustrations.
---

# Model Architecture

Create editable, standalone TikZ figures whose geometry and notation communicate the model mechanism precisely. Treat the figure as source-controlled technical content: preserve the `.tex`, compile it, render it, inspect the PNG, and repair visible defects before delivery.

## Routing boundary

- Use this skill for the internal structure of an ML/LLM model: tensors, projections, operators, attention paths, layer composition, residual connections, caches, routing, losses, and mathematically labelled mechanisms.
- Use Graphviz for software/system architecture, dependencies, infrastructure, runtime data flow, mind maps, and concept hierarchies where automatic topology layout is the main need.
- Use Mermaid for UML sequence, class, state, and activity diagrams.
- Do not select a renderer from the word `architecture` alone. `Transformer architecture` usually means this skill; `serving architecture` usually means Graphviz.

## Output contract

- Keep the editable standalone `.tex` source and compiled `.pdf` beside the rendered image.
- For Markdown, the primary artifact is a high-resolution `.png`; embed it with a standard Markdown image link. SVG is optional and should not block delivery.
- In this Obsidian vault, save task outputs under `_resources/{year}/{project}/` and reference the PNG relatively from the note.
- Do not flatten a supplied paper figure into the result. Reconstruct its semantic elements as TikZ nodes, paths, labels, patterns, and groups.

## Starting points

- For self-attention internals, start from `assets/self-attention-template.tex`.
- For the canonical encoder-decoder cross-attention sublayer, start from `assets/encoder-decoder-cross-attention-template.tex`. Its query and residual stream comes from the decoder; its keys and values come from encoder memory.
- For common model families, read [references/template-catalog.md](references/template-catalog.md), inspect the chosen template's metadata, and copy its `.tex` into the user's output directory before editing it.
- For a complex figure or screenshot reconstruction, read [references/figure-grammar.md](references/figure-grammar.md) before drawing.

## Workflow

1. Establish the semantic contract: identify every tensor or state, transformation, branch, merge, cache boundary, repeated group, and required mathematical label. When reconstructing a paper figure, summarize the source meaning before drawing and mark uncertain interpretation rather than inventing it.
2. Choose the nearest bundled template. Copy it into the task output directory and edit the copy; never edit the installed skill assets during ordinary figure work.
3. Define reusable styles and semantic node names before positioning. Keep tunable labels, dimensions, spacing, and colors in a short parameter block near the top of the file.
4. Draw primary computation flow first, then residual/bypass paths, boundaries, annotations, tensor glyphs, and legends. Draw connectors behind nodes when they would otherwise cross glyphs or labels.
5. Run `scripts/render.sh path/to/figure.tex`. This compiles with XeLaTeX and produces the PDF and Markdown-first PNG.
6. Inspect the rendered PNG with the available image viewer. Check semantic direction, missing or duplicated edges, label accuracy, clipping, overlap, ambiguous crossings, inconsistent spacing, and legibility at the intended Markdown width.
7. Make one focused repair pass after the first render. Continue only for a severe defect or incorrect model semantics, then rerun the exact render and inspection.

## Drawing rules

- Use LaTeX math for variables and operators; do not approximate mathematical notation with plain Unicode when a proper formula is available.
- Distinguish tensors, transformations, operators, and boundaries consistently. Repeated tensor slices may be shown as stacked planes or compact vector cells, but the glyph must not imply an unsupported dimensionality.
- Keep the main computation direction obvious. Use curved Bézier paths for residual or long bypass connections when they reduce crossings; prefer short straight connections inside a local operator chain.
- Use direct labels and a small color-blind-safe palette. Color should encode a stable semantic distinction and must not be the only carrier of meaning.
- Use the bundled paper-pastel palette by default: pink for learned input projections, blue or lavender for tensors and hidden states, green for score/normalization computations and the output projection, peach for the attention readout, yellow for LayerNorm, and neutral dark outlines and connectors. Depart from it only to match an explicit reference or established project palette.
- Use dashed or patterned treatment only for an explicit semantic status such as cached state, optional path, repeated block, or external context, and include a legend when that meaning is not evident.
- Preserve source semantics over pixel fidelity when recreating an image. Never silently change tensor ownership, branch direction, aggregation type, cache status, or operator order to improve layout.
- Keep prose outside the figure. Use concise labels in the image and put explanation in the surrounding note or caption.

## Completion criteria

- The `.tex` compiles without errors.
- The PDF and PNG exist and are nonblank.
- The PNG has been visually inspected after the final render.
- No text, arrowhead, boundary, or tensor glyph is clipped or unintentionally overlapped.
- The visual path agrees with the stated model computation, and any schematic or uncertain element is disclosed.
- The final response links the `.tex`, `.pdf`, and Markdown-first `.png`.
