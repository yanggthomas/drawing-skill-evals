# Model-figure grammar

## Semantic primitives

| Meaning | Preferred representation |
|---|---|
| Tensor or hidden state | Compact rounded bar, vector cells, matrix grid, or stacked planes |
| Learned transformation | Rounded rectangle labelled with the operation or projection |
| Scalar/operator | Small circle or compact mathematical node such as `$+$`, `$\times$`, `$\sigma$`, or normalization |
| Attention or compound mechanism | Wider named block receiving explicitly labelled inputs |
| Residual/bypass path | Curved Bézier connection routed outside the primary column |
| Repeated layer or head | Stacked outlines or a fitted group with `×N`; do not duplicate dozens of indistinguishable nodes |
| Cached materialization | Patterned fill or explicit cache badge, explained once in a legend |
| Semantic subsystem | Light fitted boundary drawn behind its children, optionally dashed |

## Layout order

Choose a single dominant computation direction. Place the input and output anchors first, then the main operator chain, parallel branches, merges, and long bypasses. Reserve whitespace for mathematical labels before adding decorative grouping. A branch should leave and re-enter through distinct anchors; avoid paths that cross a node or appear to terminate at a label.

## Default paper palette

Use dark neutral outlines and connectors with low-saturation pastel fills. The bundled attention templates define the canonical colors and role mapping: learned input projections are pink, tensors and hidden states are blue or lavender, score/softmax computations and the output projection are green, attention readout is peach, and LayerNorm is yellow. Keep residual paths neutral rather than assigning them a saturated accent. Color supports recognition but does not replace labels, shapes, or topology.

## Screenshot or paper reconstruction

Inventory the source figure before drawing: panels, nodes, labels, mathematical symbols, edge directions, repeated glyphs, boundaries, colors, patterns, and legend meanings. Separate semantic requirements from incidental typography or imperfect source alignment. Reproduce the former exactly and improve the latter only when the change cannot alter interpretation.

If the source is insufficient to determine an operator, tensor direction, cache boundary, or merge semantics, mark the output schematic and state the uncertainty. Visual resemblance is not evidence that the computation is correct.

## Visual QA

Inspect the rendered PNG at both full size and the intended Markdown display width. Verify that subscripts and superscripts remain legible, arrowheads are visible, parallel branches are distinguishable, long curves do not imply unintended dependencies, pattern fills survive rasterization, and no label relies on color alone.
