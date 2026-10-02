# QA — single generated image

Inspected the generated PNG visually at 1536×1024. One built-in image_gen generation call; no regeneration, editing, reference images, or image inclusion arguments.

## Correctly represented
- Forward all-gather before fc1; feature-sharded intermediate; partial-sum fc2 output; reduce-scatter to sequence-sharded output.
- Backward all-gather of dY, local fc2 and activation gradients, fc1 partial dX and reduce-scatter.
- Separate saved-input backward all-gather for dW1, correctly fed by dZ and X.
- Main tensor and weight shapes, dimension conventions, ordinary/gated distinction and assumptions are visible.
- Source citations appear in the image footer; original detailed prompt and grounding accompany it.

## Visible errors and limitations
- The fc2 weight-gradient output is labeled dW_r rather than the requested dW2_r. Its location and [h,f/p] shape identify it, but the missing “2” is a labeling error.
- The partial-input-gradient label contains an awkward redundant/superscript rank marker; intended meaning is dX_partial_r.
- The generator added dW1_r = dZ_r^T X without explicitly stating that s and b are flattened/contracted. The formula is valid in the flattened GEMM convention used in the code, but ambiguous alongside three-dimensional tensor labels.
- Bottom notes and source citations are relatively small at native resolution.
- Bias gradients and optional execution variants are intentionally outside the declared main-path scope.

No corrections were applied, per the single-call constraint.

## Tool-handling incident
The generation result was accidentally passed to text(), which printed a truncated base64 image payload to tool output. The generated file itself is intact; no second call was made. Subsequent inspection used only the saved file path and metadata. This violated the requested no-base64-printing constraint and is recorded honestly.
