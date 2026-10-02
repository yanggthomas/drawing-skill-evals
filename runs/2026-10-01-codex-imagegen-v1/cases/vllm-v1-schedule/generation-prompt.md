Use case: infographic-diagram.
Generate one polished high-resolution landscape technical diagram, approximately 2400x1600, white background, crisp dark typography, restrained teal/blue for running requests, gold for waiting requests, coral for preemption. Title "vLLM V1 · One scheduler step". Subtitle "Continuous batching: one shared token budget, running requests first". This is an engineering explanatory figure, all text legible, no decorative graphics.
Compose three horizontal regions: upper main control flow (left to right); middle allocation and preemption branch; bottom numeric worked example and output payload. Clear arrows, no crossings, generous margins. Render source references as small readable captions.

Main flow:
1. "Start step" with "B = max_num_scheduled_tokens" and "I = max_num_batched_tokens". Small note "B: scheduled-token budget · I: model-input budget". source "scheduler.py:583–586".
2. "RUNNING first" with formula "need = tokens_with_spec + output_placeholders − computed"; below "n = min(need, B, I − draft_slots, optional long-prefill cap)" and "also respect model-length / specialized constraints". Caption "scheduler.py:629–690". Each running candidate points down to a KV allocation node and successful allocation loops back to "record n; B −= n; I −= n + draft_slots" then next running request. Clear success label.
3. Gate "No preemption this step?" YES arrow to "WAITING / PREEMPTED admission". NO bypass to output. Waiting text "Use remaining B and I; respect active-request limit" / "KV-holding queue first; skip blocked requests" / "Prefix-cache lookup → reduce uncomputed work" / "Clip n to remaining budget when chunking enabled". Small note "Chunking disabled and prompt does not fit → stop admission". source "scheduler.py:873–938, 1074–1125". Waiting node points to same KV manager with labeled arrow "allocate before admission"; successful waiting allocation arrow to "Move to RUNNING; record n; debit budgets". Failed waiting allocation arrow labeled "None → stop admission (no eviction here)" leading to output. source "scheduler.py:1211–1232, 1292–1318".

Middle:
Large box "KVCacheManager.allocate_slots()" with small block diagram of existing blocks + prefix-hit blocks + newly allocated blocks. Text "Capacity check → adopt cached blocks → allocate new blocks" / "Returns block IDs, or None if insufficient capacity" / "Token budgets and KV capacity are separate limits". caption "kv_cache_manager.py:558–614".
From RUNNING allocation failure only, coral arrow into "Preempt a RUNNING victim" box:
"FCFS: tail of running list"
"Priority: max(priority, arrival_time)"
"Free request KV / encoder cache; computed = 0"
"status = PREEMPTED; prepend to waiting"
"Restore this step's budgets if victim was already scheduled"
Then retry arrow back to KV allocation labeled "Retry; stop if current request is victim or blocks cannot be freed now". Note "Any preemption skips waiting admission this step." source "scheduler.py:764–818, 874, 1558–1583".
Do not imply preemption swaps KV to CPU. Do not imply every insufficient allocation can preempt: caption "Pending connector frees / unsafe immediate free may stop retry".

Bottom left worked example under "Example · chunked prefill continues across steps":
"Assume B = I = 8; chunking on; cap off; no cache hits, spec tokens or special gates."
Visual single 8-slot budget strip: 1 blue slot A, 3 teal slots B, 4 gold slots C. Label "A: decode 1  +  B: running prefill 3  +  C: waiting prompt 4  =  8".
C prompt strip of 10 token cells: first four colored gold and six gray, brackets "step t: 4" and "remaining: 6".
Arrow to small next-step box "C stays RUNNING; computed = 4" / "step t+1: remaining 6 eligible for budget".
Caption "After output construction: computed += n (optimistic); later output may correct it." source "scheduler.py:1585–1605". Clearly example values are illustrative, not defaults.

Bottom right "SchedulerOutput → Model runner" box:
"new requests: full metadata + block IDs"
"cached requests: request / block-table updates"
"num_scheduled_tokens = {A:1, B:3, C:4}"
"total_num_scheduled_tokens = 8"
"also: spec / encoder work, common-prefix blocks,"
"finished IDs and preempted IDs"
Small note "V2 runner sends resumed requests as new data."
Caption "output.py:232–272; scheduler.py:1379–1409, 1463–1479".
Footer "Source snapshot: 4c2d277643e2 · Core text path shown; optional features summarized."
All elements must fit within one image. Exact program identifier spelling. Avoid conflating all RUNNING with decode, or assuming WAITING always receives tokens. Main point is scheduling token work and allocating KV blocks before a model execution.
