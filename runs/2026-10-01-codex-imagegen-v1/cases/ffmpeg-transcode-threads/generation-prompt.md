Use case: infographic-diagram.
Create ONE precise, beautiful raster technical diagram, landscape 2400x1600 or larger, white background, crisp dark sans serif typography, restrained teal/navy/amber palette. Title "FFmpeg: threaded transcoding". Subtitle "fftools • a344f0976c5d • task threads, bounded queues, feedback control". No photographs or decoration.

Compose a large upper pipeline occupying 55% of canvas and two spacious explanatory panels below. Five equal columns represent actual task threads, with pale blue thread cards and white queue cards between. Thread headings, left to right: "Demuxer", "Decoder", "Filtergraph", "Encoder", "Muxer". Beneath each heading small labels: "per input file", "per decoder", "per filtergraph", "per encoder", "per output file". One scheduler task pthread per component instance; codec/filter internal workers are outside this view. Draw data arrows LEFT TO RIGHT with visible arrowheads. Main chain:
Input → Demuxer → [packet ThreadQueue] → Decoder → [frame ThreadQueue] → Filtergraph → [frame ThreadQueue] → Encoder → [packet ThreadQueue] → Muxer → Output.
Queues may be slim stacked-slot icons with clear labels placed underneath, to give enough room. Packet arrows navy labeled "AVPacket"; frame arrows teal labeled "AVFrame". Under Muxer label "interleave + write". Add a separate navy stream-copy branch from Demuxer going below the central thread cards and joining the SAME packet queue before Muxer; label "stream copy • packets bypass decode / filter / encode". Route it cleanly without obscuring any labels.

Under pipeline add two small optional buffering notes connected by fine leader lines: at encoder input "Optional pre-encode SyncQueue"; at mux input "PreMuxQueue until mux startup"; within mux thread small note "Optional packet SyncQueue". Optional SyncQueues are buffering helpers, NOT threads and NOT ThreadQueues.

Immediately below pipeline put a thin amber control strip "Scheduler — shared state + APIs, not a separate worker thread". Dashed amber feedback arrow from mux-input send point to strip labeled "per-stream DTS + duration". Dashed amber control arrows from strip up to Demuxer and Filtergraph labeled "choke / unchoke". All thread communication goes via scheduler APIs; visible arrows are logical data paths.

Lower left panel titled "Bounded queues → backpressure". Include four concise lines:
"Default: 2 items per stream; mux queue configurable."
"Full stream queue: tq_send() sleeps."
"Consumer pops → wakes blocked producer."
"Empty or choked queue: receiver waits; EOF wakes peers."
Small miniature producer→two-slot queue→consumer schematic; reverse dotted arrow labeled "wake". Do not confuse this with scheduler synchronization.

Lower right panel titled "Keep output progress aligned". Numbered statements:
"1  Track latest DTS + duration at each mux input."
"2  Find trailing unfinished output across all muxers."
"3  Unchoke sources less than 100 ms ahead."
"4  Trace filter best_input upstream; keep draining paths live."
Additional small note: "Unknown timestamps get priority. Muxers are never choked."
Additional boundary note: "Rate control is approximate; input interleaving can still force buffering."

Footer key: "Solid arrows: media • Dashed amber: scheduling • Queue cards: shared buffers". Footer source citations compact but legible: "ffmpeg_sched.h:34–85,254–262 | ffmpeg_sched.c:404–424,438–457,1314–1509,2009–2059 | thread_queue.c:143–179,188–299 | ffmpeg_mux.c:232–271". These citations ground diagram rather than look like UI links. Prioritize correct unambiguous topology, no arrow crossing text, clear margins and readable typography. Do not invent a scheduler thread or a queue before demux. This is one representative A/V transcode plus stream-copy path; arbitrary fan-out and subtitle exceptions are intentionally omitted.
