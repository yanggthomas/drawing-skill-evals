"""G3 golden: FFmpeg CLI threaded transcoding as a data pipeline plus the Scheduler that controls it.

Top: the media row, left to right. Bottom: the Scheduler drawn as structure, not prose: the state it
keeps (waiters, per-stream progress) and its decision function, wired to what it reads and what it blocks.
Facts: evals/ffmpeg-transcode-threads/src/fftools (FFmpeg a344f09).
Run: ~/.uve/model_viz/bin/python g3_transcode_threads.py  ->  g3-transcode-threads.png / .pdf
"""

from svgkit import FAINT, INK, MUTED, Canvas, block_height, width

THREAD = ("#E1BEE7", "#6A1B9A")
QUEUE = ("#FFF2B2", "#B8860B")
ACCENT = ("#F4D35E", "#D68A1A")
PRIMARY = ("#F4A261", "#E76F51")
WAITER = ("#FFF4D6", "#D68A1A")
PKT, FRM, COPY, FULL, CTRL = "#2E86AB", "#6A1B9A", "#E76F51", "#C0392B", "#B8740F"

W, H = 2060, 900
c = Canvas(W, H)


def B(s, size=15): return (s, "b", size, INK)
def R(s, size=13): return (s, "r", size, INK)
def M(s, size=13): return (s, "m", size, INK)
def REF(s): return (s, "m", 10, MUTED)


# ── row geometry ──────────────────────────────────────────────────────────────
TOP, CARD_H, TW, GAP = 236, 128, 172, 40
CY = TOP + CARD_H / 2
row, x = {}, 40
for name, w in [("demux", TW), ("decq", 118), ("dec", TW), ("fq", 140), ("filt", TW),
                ("encq", 118), ("enc", TW), ("send", 150), ("muxq", 140), ("mux", TW)]:
    row[name] = (x, w)
    x += w + GAP


def left(n): return row[n][0]
def right(n): return row[n][0] + row[n][1]
def mid(n): return row[n][0] + row[n][1] / 2


HEX_H, HEX_K = 110, 22


def hex_inset(y):
    return HEX_K * abs(y - CY) / (HEX_H / 2)


# ── title ─────────────────────────────────────────────────────────────────────
c.text(40, 50, "FFmpeg CLI: threaded transcoding and the Scheduler that keeps outputs in step", 30, "b")
c.text(40, 82, "Each component runs in its own thread and talks only to Scheduler-owned queues. The Scheduler is not a thread: "
       "it watches output progress and blocks sources that run ahead.", 16, "r", MUTED)

# ── media data plane ──────────────────────────────────────────────────────────
c.rect(20, 108, W - 40, 356, "#FAFCFD", "#B9CCD8", r=14, sw=1.4)
c.text(40, 134, "MEDIA DATA PLANE", 15, "b", "#46606F")
c.text(52 + width("MEDIA DATA PLANE", "b", 15), 134,
       "packets and frames move left to right; every queue is a bounded ThreadQueue owned by the Scheduler", 14, "r", MUTED)

THREADS = {
    "demux": ("input_thread", "one per input file", ["av_read_frame()", "→ sch_demux_send()"], "ffmpeg_demux.c:843"),
    "dec": ("decoder_thread", "one per decoded stream", ["sch_dec_receive()", "→ decode", "→ sch_dec_send()"], "ffmpeg_dec.c:909"),
    "filt": ("filter_thread", "one per filtergraph", ["sch_filter_receive()", "→ filter", "→ sch_filter_send()"], "ffmpeg_filter.c:3443"),
    "enc": ("encoder_thread", "one per encoded stream", ["sch_enc_receive()", "→ encode", "→ sch_enc_send()"], "ffmpeg_enc.c:1009"),
    "mux": ("muxer_thread", "one per output file", ["sch_mux_receive()", "→ interleave", "→ write to file"], "ffmpeg_mux.c:403"),
}
for n, (name, count, calls, ref) in THREADS.items():
    c.rect(left(n), TOP, TW, CARD_H, *THREAD, r=10, sw=1.5)
    rows = [B(name), (count, "r", 12, MUTED)]
    rows += [M(s) if "(" in s else R(s, 14) for s in calls] + [REF(ref)]
    c.lines(left(n) + 12, TOP + 3, rows)

QUEUES = {
    "decq": ["packet queue", "AVPacket", "2 slots"],
    "fq": ["frame queue", "1 stream per input", "+ control · 2 slots"],
    "encq": ["frame queue", "AVFrame", "2 slots"],
    "muxq": ["packet queue", "1 stream per", "output stream", "2 slots by default", "(-thread_queue_size)"],
}
QH = 118
for n, rows in QUEUES.items():
    qx, qw = row[n]
    c.cylinder(qx, CY - QH / 2, qw, QH, *QUEUE)
    spec = [B(rows[0], 14)] + [R(s, 12 if len(s) > 18 else 13) for s in rows[1:]]
    c.lines(qx + qw / 2, CY - block_height(spec) / 2 + 6, spec, anchor="middle")

c.hexagon(left("send"), CY - HEX_H / 2, row["send"][1], HEX_H, *ACCENT, k=HEX_K)
c.lines(mid("send"), CY - 42, [B("send_to_mux()"), R("runs in the", 13), R("sending thread", 13),
                               REF("ffmpeg_sched.c:2009")], anchor="middle")

# forward data (upper lane) and "queue full: sender blocks" (lower lane)
FWD, BACK = CY - 10, CY + 14
for a, b, color in [("demux", "decq", PKT), ("decq", "dec", PKT), ("dec", "fq", FRM), ("fq", "filt", FRM),
                    ("filt", "encq", FRM), ("encq", "enc", FRM), ("enc", "send", PKT), ("send", "muxq", PKT),
                    ("muxq", "mux", PKT)]:
    yy = FWD if b in QUEUES or a == "enc" else CY
    x0 = right(a) - (hex_inset(yy) if a == "send" else 0)
    x1 = left(b) + (hex_inset(yy) if b == "send" else 0) - 2
    c.arrow([(x0, yy), (x1, yy)], color)
for producer, q in [("demux", "decq"), ("dec", "fq"), ("filt", "encq"), ("send", "muxq")]:
    x1 = right(producer) - (hex_inset(BACK) if producer == "send" else 0) + 2
    c.arrow([(left(q), BACK), (x1, BACK)], FULL, sw=1.8, dash="6 4")
    c.text((right(producer) + left(q)) / 2, BACK + 20, "full", 11, "r", FULL, "middle")

# stream copy and subtitles bypass above the row
COPY_Y, SUB_Y = 166, 200
c.arrow([(mid("demux"), TOP), (mid("demux"), COPY_Y), (mid("send"), COPY_Y), (mid("send"), CY - HEX_H / 2 - 2)], COPY, sw=3.2)
c.tag((mid("demux") + mid("send")) / 2, COPY_Y + 4,
      "STREAM COPY: the demuxed AVPacket goes straight to send_to_mux(), no decode / filter / encode", COPY, 14, "b",
      bg="#FAFCFD")
c.arrow([(mid("dec") + 30, TOP), (mid("dec") + 30, SUB_Y), (mid("encq"), SUB_Y), (mid("encq"), CY - QH / 2 - 2)],
        FRM, sw=1.6, dash="6 4")
c.tag((mid("dec") + mid("encq")) / 2, SUB_Y + 4, "subtitle frames skip the filtergraph", FRM, 13, bg="#FAFCFD")

# pre-mux buffering before the muxer starts
LOW = 418
c.cylinder(left("muxq") - 10, LOW - 26, row["muxq"][1] + 20, 56, "#FFF9DB", QUEUE[1], dash="5 3", ry=6)
c.lines(mid("muxq"), LOW - 14, [B("pre-mux FIFO", 12), R("until the muxer starts", 11)], anchor="middle")
c.arrow([(mid("send") + 34, CY + HEX_H / 2 - 6), (mid("send") + 34, LOW), (left("muxq") - 12, LOW)], PKT, sw=1.6, dash="6 4")
c.arrow([(mid("muxq"), LOW - 26), (mid("muxq"), CY + QH / 2 + 2)], PKT, sw=1.6, dash="6 4")

# ── Scheduler: state + decision, wired to the pipeline ────────────────────────
SY = 488
c.rect(20, SY, W - 40, 318, "#FFFAF4", PRIMARY[1], r=14, sw=1.8)
c.text(40, SY + 26, "SCHEDULER", 15, "b", "#B4462B")
c.text(52 + width("SCHEDULER", "b", 15), SY + 26,
       "one shared object, not a thread: its functions run inside whichever thread calls them, under schedule_lock",
       14, "r", MUTED)

# per-output-stream progress (written by send_to_mux)
PX, PY, PW, PH = 1330, 650, 250, 100
c.rect(PX, PY, PW, PH, "white", PRIMARY[1], r=8, sw=1.5)
c.lines(PX + 12, PY + 4, [B("per output stream", 14), M("last_dts = dts + duration", 12), M("finished  (EOF seen)", 12),
                          REF("ffmpeg_sched.c:2050-2057")])

# the decision function
HX, HY, HW, HH = 860, 640, 380, 124
c.hexagon(HX, HY, HW, HH, *PRIMARY, k=30)
c.lines(HX + HW / 2, HY + 10, [("schedule_update_locked()", "m", 15, INK),
                               R("trailing = smallest last_dts of unfinished streams", 12),
                               R("unchoke the sources of streams < 100 ms ahead,", 12),
                               R("choke the rest; at least one source always runs", 12),
                               REF("ffmpeg_sched.c:1422-1520")], anchor="middle")

# waiters: the Scheduler-owned gates the sources block on
def waiter(cx, title, sub):
    w = 226
    c.rect(cx - w / 2, 548, w, 60, *WAITER, r=8, sw=1.6)
    c.lines(cx, 550, [B(title, 13), R(sub, 11), REF("SchWaiter: choked flag + condvar")], anchor="middle")


waiter(mid("demux") + 20, "demuxer waiter", "one per input file")
waiter(mid("filt"), "filtergraph waiter", "used by input-less graphs")

# ① send_to_mux records progress  → ② feeds the decision → ③ waiter_set → ④ sources block or resume
c.arrow([(mid("send") - 20, CY + HEX_H / 2 - 4), (mid("send") - 20, PY - 2)], CTRL, sw=2.4, dash="8 5")
c.badge(mid("send") - 20, 584, "1", CTRL)
c.tag(mid("send") - 2, 589, "every packet or EOF", CTRL, 13, "b", anchor="start", bg="#FFFAF4")

c.arrow([(PX, 700), (HX + HW + 2, 700)], CTRL, sw=2.4, dash="8 5")
c.badge((PX + HX + HW) / 2, 700, "2", CTRL)

c.badge(HX + HW / 2, HY + HH + 18, "3", CTRL)
c.text(HX + HW / 2 + 18, HY + HH + 23, "decide", 13, "b", CTRL)

c.arrow([(HX, 702), (mid("demux"), 702), (mid("demux"), 610)], CTRL, sw=2.4, dash="8 5")
c.badge(560, 702, "4", CTRL)
c.tag(580, 707, "waiter_set(): choke / unchoke", CTRL, 13, "b", anchor="start", bg="#FFFAF4")
FW_X = HX + 70                                    # on the hexagon's top edge, under the filtergraph waiter
c.arrow([(FW_X, HY), (FW_X, 610)], CTRL, sw=2.4, dash="8 5")
c.badge(FW_X - 20, 625, "4", CTRL, r=10, size=11)

c.arrow([(mid("demux"), 548), (mid("demux"), TOP + CARD_H + 2)], CTRL, sw=2.4, dash="8 5")
c.badge(mid("demux"), 476, "5", CTRL)
c.tag(mid("demux") + 18, 400, "sch_demux_send()", CTRL, 12, "m", anchor="start", bg="#FAFCFD")
c.tag(mid("demux") + 18, 416, "blocks in waiter_wait()", CTRL, 12, anchor="start", bg="#FAFCFD")
c.arrow([(mid("filt"), 548), (mid("filt"), TOP + CARD_H + 2)], CTRL, sw=2.4, dash="8 5")
c.tag(mid("filt") - 10, 418, "sch_filter_receive() waits", CTRL, 12, anchor="end", bg="#FAFCFD")

# choking a demuxer also chokes the queues it feeds, so their readers stop draining them
qx = mid("decq")
c.arrow([(mid("demux") + 133, 578), (qx + 20, 578), (qx + 20, CY + QH / 2 + 2)], CTRL, sw=1.8, dash="3 4")
c.tag(qx + 28, 540, "tq_choke(): its readers", CTRL, 12, anchor="start", bg="#FFFAF4")
c.tag(qx + 28, 556, "get EAGAIN, stop draining", CTRL, 12, anchor="start", bg="#FFFAF4")

# a filtergraph changing the input it wants also re-runs the decision
BI_Y, BI_X = 436, HX + HW - 60                       # along the data plane's floor, down onto the hexagon's top edge
c.arrow([(mid("filt") + 50, TOP + CARD_H), (mid("filt") + 50, BI_Y), (BI_X, BI_Y), (BI_X, HY - 2)], CTRL, sw=1.8, dash="8 5")
c.tag((mid("filt") + 50 + BI_X) / 2 + 20, BI_Y - 8, "best input changed", CTRL, 12, bg="#FAFCFD")

# ── key and footer ────────────────────────────────────────────────────────────
ky = 838
x = 40
for color, dash, sw, label in [(PKT, None, 2.0, "AVPacket"), (FRM, None, 2.0, "AVFrame"), (COPY, None, 3.2, "stream copy"),
                               (FULL, "6 4", 1.8, "queue full: the sender blocks in tq_send()"),
                               (CTRL, "8 5", 2.4, "Scheduler: progress in, choke / unchoke out")]:
    c.arrow([(x, ky), (x + 40, ky)], color, sw=sw, dash=dash)
    c.text(x + 50, ky + 5, label, 14)
    x += 50 + width(label, "r", 14) + 44
c.text(40, 872, "Threads start in sch_start(): encoders, filtergraphs, decoders, then demuxers; a muxer starts once all its "
       "streams are ready. Optional SyncQueue and codec-internal threads not shown.", 12, "r", MUTED)
c.text(40, 890, "Source: FFmpeg fftools @ a344f09 · ffmpeg_sched.c, thread_queue.c, ffmpeg_{demux,dec,filter,enc,mux}.c",
       11, "m", FAINT)

print(*c.save("g3-transcode-threads"))
