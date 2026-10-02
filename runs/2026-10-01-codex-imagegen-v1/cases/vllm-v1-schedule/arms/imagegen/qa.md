# Single-sample visual QA

Built-in image generation was called exactly once, without reference images. The returned image was inspected inline at its native 1536 x 1024 display. No regeneration or raster editing was performed. Original generated PNG copied to out/schedule-step.png.

## Observed strengths

- Text is largely legible, with good group separation and consistent request colors.
- Running-first order, dual budgets, prefix reuse, chunking, preemption victim policies, reset/requeue behavior, and output payload are represented.
- The example conserves 8 tokens (1 + 3 + 4) and shows a 10-token prompt split into 4 processed and 6 pending.
- The figure explicitly labels illustrative assumptions and optimistic progress.

## Observed defects and limitations

- The NO branch from the preemption gate is labeled correctly as bypassing waiting admission, but its arrow incorrectly terminates at KVCacheManager rather than directly at output construction. This is a material control-flow ambiguity.
- Running success and waiting success/failure branches visually originate at the request-slot nodes, instead of unambiguously emerging from KVCacheManager. Their labels communicate the intended result but arrow topology is imprecise.
- The preemption box has a direct downward arrow to output in addition to retry; the precise break condition is only conveyed in the retry annotation.
- Running allocation node cites scheduler.py:629–690, which covers candidate token calculation but not allocation (actual allocation is 745–752). The grounding file supplies the correct allocation range.
- Formula uses compact aliases tokens_with_spec/output_placeholders/computed rather than literal Request field names. Main caption and grounding describe their intended meanings.
- Active unpaused gating and optional specialized mechanisms are summarized or omitted; this is a core text path illustration, not exhaustive execution flow.

This is retained as the one-shot evaluation result, not represented as error-free.
