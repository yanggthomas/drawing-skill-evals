---
type: llm
focus: { source: file, path: out/transcode-threads.png }
---

You are grading a diagram (the attached PNG) that is meant to explain the threaded transcoding pipeline in `fftools` (FFmpeg master). Judge only what the picture shows. Do not credit anything you would have to infer from code that is not drawn. Exact identifiers are not required when the mechanism is drawn unambiguously.

Reference facts:

1. **Scheduler in the middle.** Demuxers, decoders, filtergraphs, encoders and muxers never talk to each other directly. Every send and receive goes through the `Scheduler`, which is the only object that knows the whole graph (a DAG, checked at start).
2. **One thread per component.** Each demuxer, decoder, filtergraph, encoder and muxer runs in its own thread: `input_thread`, `decoder_thread`, `filter_thread`, `encoder_thread`, `muxer_thread`. `sch_start` creates them muxers first and demuxers last.
3. **Queues sit at the consumer's input.** Queues: each decoder has a packet queue, each filtergraph a frame queue (one stream per input plus a control stream), each encoder a frame queue, each muxer a packet queue with one stream per output stream. The demuxer has no input queue.
4. **Data path.** Packets go demux → decoder → frames → filtergraph → encoder → packets → muxer. For stream copy, demuxed packets go straight to the muxer. Subtitle frames skip filtering and go decoder → encoder.
5. **Thread loop.** Each worker thread loops: receive from its own input queue (`sch_*_receive`), process, then send downstream (`sch_*_send`, which pushes into the next thread's queue).
6. **Bounded queues = backpressure.** Queues are tiny (2 entries by default for packets and for frames), and `tq_send` blocks while the destination is full. A slow consumer therefore stalls its producers.
7. **Sync by muxer DTS.** Each packet that reaches a muxer stream updates that stream's `last_dts` and calls `schedule_update_locked`. That function finds the trailing output DTS and unchokes only the sources (demuxers / source filtergraphs) feeding streams that are less than `SCHEDULE_TOLERANCE` (100 ms) ahead of it. At least one source always stays unchoked.
8. **Choking a demuxer.** A choked demuxer blocks on a condition variable in `waiter_wait` at the start of `sch_demux_send`. Choking it also chokes the queues it feeds (`tq_choke`), so downstream threads don't drain them.

For each fact, decide: SHOWN (drawn correctly), ABSENT (not drawn), or CONTRADICTED (drawn in a way that conflicts with the fact). Examples of a contradiction: components call each other directly instead of through the scheduler; demuxers have an input queue; a full queue drops data instead of blocking.

PASS if at least 6 of the 8 facts are SHOWN and none is CONTRADICTED.
FAIL otherwise. Begin your explanation by listing the SHOWN / ABSENT / CONTRADICTED verdict for each fact number.
