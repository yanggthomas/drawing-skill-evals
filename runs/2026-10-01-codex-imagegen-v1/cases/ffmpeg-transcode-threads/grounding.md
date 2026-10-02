# Grounding

Scope: representative audio/video path plus stream copy, at src/PINNED.txt commit a344f0976c5d0fc736715b3a63b0128f90c56377. Only prompt.md and src/** were inspected.

- Component topology and scheduler-mediated communication: src/fftools/ffmpeg_sched.h:34–85. Instance multiplicity derives from component model, not five globally fixed threads.
- Task pthread creation: src/fftools/ffmpeg_sched.c:404–424. Actual functions input_thread (ffmpeg_demux.c:843), decoder_thread (ffmpeg_dec.c:909), filter_thread (ffmpeg_filter.c:3443), encoder receive loop (ffmpeg_enc.c:1037), mux receive loop (ffmpeg_mux.c:422).
- Decoder packet queue: ffmpeg_sched.c:802; encoder frame queue:846; filter multi-input frame queue:894; mux multi-stream packet queue:1703. Paths documented ffmpeg_sched.h:35–53. All referenced files under src/fftools/.
- Default capacities 2: ffmpeg_sched.h:254–262; per-stream capacity and blocking: thread_queue.c:143–164; consumption wakes upstream:203–205; empty/choked blocking:193–194,234–247; EOF handling:258–284.
- Pre-mux buffering and startup drain: ffmpeg_sched.c:1135–1184,2017–2048; optional pre-encoding SyncQueue:1840–1851,1877 onward; optional mux SyncQueue and final interleave: ffmpeg_mux.c:232–271.
- Output timestamp means DTS + duration normalized to microseconds at send_to_mux, not disk-write completion: ffmpeg_sched.c:2009–2059.
- Minimum unfinished output DTS: ffmpeg_sched.c:438–457; 100 ms tolerance:44–46; eligibility and unknown-timestamp behavior:1422–1467. Backtrack best_input, unblock downstream, never choke muxers:1314–1390. Queue choking:1392–1419. At-least-one-source fallback:1483 onward.
- Approximate synchronization and interleaving limitation: ffmpeg_sched.h:63–71.

Assumptions / omissions: diagram is a representative A/V pipeline with a stream-copy branch, not complete graph enumeration. Codec/filter internal worker pools, subtitle bypass, loopback decoder branches, arbitrary graph fan-out, detailed init/EOF protocol omitted for readability. Optional SyncQueue implementations are not vendored and their internals are not asserted. Shared scheduler is shown as control strip; no separate scheduling worker is asserted.
