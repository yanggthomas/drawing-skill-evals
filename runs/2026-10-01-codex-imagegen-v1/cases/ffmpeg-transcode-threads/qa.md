# Single-sample visual QA

Generated with one built-in imagegen call, no image references, no regeneration. Inspected the returned image visually. Original retained in the built-in generated-images directory and copied without editing to out/transcode-threads.png.

## Observed strengths

- Five component thread cards and four interposed typed ThreadQueues are visible and readable. Packet / frame transitions and the stream-copy branch joining the mux input queue are correctly represented.
- Shared scheduler explicitly says it is not a separate worker thread. Backpressure and timestamp rate control have separate explanations.
- Default queue capacity, configurability of mux queue, per-stream bounds, 100 ms tolerance, best_input tracing, interleaving limitation, and muxer non-choking appear in readable text.
- Source citation footer and pinned commit prefix are present. No text clipping or major overlapping labels observed.

## Limitations retained without correction

- Amber timestamp feedback is drawn with arrowheads at both ends, and its top endpoint visually touches the muxer card rather than the mux-input send point. This can suggest scheduler-to-mux control even though the text correctly states muxers are never choked. Intended direction was mux-input timestamp update to scheduler only.
- Main queue icons show three slots while text says default 2; icons should be read as generic queue symbols, but the visual count is inconsistent. The lower backpressure inset correctly shows two slots.
- Optional pre-encode SyncQueue leader points near the encoder card, without explicitly ordering it before the encoder ThreadQueue. It is an annotation, not a fully specified optional path.
- Scheduler control paths cross the stream-copy line visually. Colors distinguish them, but the filter control arrow is split near that crossing.
- Internal worker pools and explicit one-pthread-per-component note requested in the generation prompt are not rendered; the card multiplicity labels and title carry the thread interpretation.
- The image is a representative A/V path, omitting graph fan-out, subtitles and loopback paths as disclosed in grounding.md.

Result: usable and substantially source-grounded, with the retained directional ambiguity and schematic limitations above. No claim of pixel-perfect or exhaustive topology accuracy.
