# Visual QA

Inspected the actual image returned by the built-in tool. Exactly one generation call; no reference images, no editing or regeneration. Original copied unchanged to out/mixed-batch-attn.png.

## Correct and legible

The four-panel diagram shows two requests, the four flattened tokens in order, correct request/query/absolute-position arrays, query_start_loc=[0,1,4], seq_lens=[6,17], physical block rows [7] and [2,9], and correct slots [117,46,47,144]. The logical-to-physical boundary crossing for B16 is explicit. Separate cache update and attention read stages are present. All four causal visible ranges are correct and exclude cross-request attention. Metadata aliases and output order are legible. Source line citations and illustrative-value footer are present.

## Errors / limitations

- The generated layer-produces-Q,K,V box appends one shared shape [4,Hq,D]. This is accurate for Q but can falsely imply K/V use Hq rather than Hkv for grouped-query attention. Supplied prompt asked only Q to have that shape; the model extended it.
- Panel 3 routes a combined “Flattened tokens and slot_mapping” arrow into the conceptual projection box. Slot mapping actually feeds cache update, not QKV projection. The scatter arrow is labelled correctly, but the drawn incoming routing is misleading.
- Physical block 2 contains an ellipsis cell after B15. With block size 16, B15 fills the final slot; there are no subsequent unused slots in that block. Text and numerical mapping are correct, but the compressed strip is visually inaccurate at its right edge.
- The page-to-cache and cross-panel flows rely partly on “from panel” labels rather than continuous connecting arrows. The evidence citations show basename and ranges, with full source mapping in grounding.md.
- The title and technical text are readable at original size, but smaller citations require zooming. No runtime validation was performed; the supplied source was statically inspected.

No corrections were made because this evaluation requires preserving the single generated result.
