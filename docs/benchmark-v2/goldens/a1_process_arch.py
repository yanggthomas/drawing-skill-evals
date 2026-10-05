"""A1 golden: vLLM V1 serving on one node (TP = N, multiprocess executor) as a deployment diagram.

Columns are OS processes, gutters hold the links between them, and every boundary-crossing link
names its transport and payload. The one broadcast queue (gold) and each worker's own reply queue
(purple, the worker colour) are drawn apart. Numbered badges are the answer-key fact numbers; the
code anchors at the bottom give their source lines. Facts: evals/vllm-v1-process-arch/src (vLLM 4c2d277).
Run: ~/.uve/model_viz/bin/python a1_process_arch.py  ->  a1-process-arch.png / .pdf
"""

from svgkit import FAINT, INK, MUTED, Canvas, width

FRONT = ("#D6EAF8", "#2E86AB", "#F8FBFD", "#EAF4FB")    # band, stroke, body, card
CORE = ("#F9D9C0", "#E76F51", "#FFFAF6", "#FDEBDD")
WORK = ("#EBD7F0", "#6A1B9A", "#FCF9FD", "#F3E5F5")
GPU = ("#FFF2B2", "#B8860B")
QUEUE = ("#FFF9DB", "#B8860B")
ZMQ, BCAST, REPLY, NCCL, LIFE, LOCAL = "#2E86AB", "#B8860B", "#6A1B9A", "#C0392B", "#8c959f", "#555555"
BADGE = "#3b6fb6"

c = Canvas(2040, 976)


def B(s, size=15): return (s, "b", size, INK)
def R(s, size=13): return (s, "r", size, INK)
def M(s, size=12): return (s, "m", size, INK)
def NOTE(s, size=12): return (s, "r", size, MUTED)


def card(x, y, w, h, fill, stroke, rows, badge=None, pad=12):
    c.rect(x, y, w, h, fill, stroke, r=8, sw=1.3)
    c.lines(x + pad, y + 4, rows)
    if badge:
        c.badge(x + w - 14, y + 14, badge, BADGE, r=10, size=11)


def column(x, w, h, palette, title, sub, count):
    c.panel(x, 146, w, h, palette[0], palette[1], palette[2], band_h=50)
    c.text(x + 16, 177, title, 19, "b")
    c.text(x + 26 + width(title, "b", 19), 177, sub, 14, "r", MUTED)
    c.pill(x + w - 14, 171, count, "white", palette[1])


def link_card(x, y, w, h, color, rows, dash=None, badge=None):
    c.rect(x, y, w, h, "white", color, r=8, sw=1.6, dash=dash)
    c.lines(x + w / 2, y + 4, rows, anchor="middle")
    if badge:
        c.badge(x + w - 4, y - 2, badge, BADGE, r=10, size=11)


# ── title ─────────────────────────────────────────────────────────────────────
c.text(40, 50, "vLLM V1 on one node: which OS processes exist and what crosses between them", 30, "b")
c.text(40, 82, "Tensor parallelism N with the multiprocess executor (DP = 1, PP = 1). Structure, not step order.", 16, "r", MUTED)
c.pill(2000, 76, "3 process roles · N + 2 OS processes", "white", INK, size=13)

c.rect(24, 104, 1992, 682, "white", "#AAB4BE", r=16, sw=1.4, dash="7 5")
c.text(44, 128, "ONE HOST", 13, "b", MUTED)
COL_H = 620

# ── column 1: frontend process ────────────────────────────────────────────────
column(50, 470, COL_H, FRONT, "Frontend process", "the API server", "1 process")
c.rect(66, 212, 438, 308, FRONT[3], FRONT[1], r=10, sw=1.2)
c.text(82, 236, "AsyncLLM", 16, "b")
c.text(92 + width("AsyncLLM", "b", 16), 236, "the EngineClient the HTTP routes call", 13, "r", MUTED)
c.badge(488, 230, "1", BADGE, r=10, size=11)

card(78, 252, 204, 74, "white", FRONT[1], [B("InputProcessor", 14), R("tokenize, preprocess", 12), M("→ EngineCoreRequest", 11)], "2")
card(78, 342, 204, 74, "white", FRONT[1], [B("output_handler", 14), R("asyncio task: pulls", 12), M("EngineCoreOutputs", 11)])
card(300, 252, 192, 164, "white", FRONT[1],
     [B("AsyncMPClient", 14), NOTE("engine-core client", 11), M("ROUTER", 12), R("sends requests", 12),
      M("PULL", 12), R("receives outputs", 12), R("msgpack codec", 12)], "3")
card(78, 432, 414, 74, "white", FRONT[1], [B("OutputProcessor", 14), R("incremental detokenizer and one output queue per request;", 12),
                                           R("results go back to the HTTP handlers", 12)], "2")
c.arrow([(282, 289), (298, 289)], LOCAL, sw=1.6)
c.arrow([(300, 379), (284, 379)], LOCAL, sw=1.6)
c.arrow([(180, 416), (180, 430)], LOCAL, sw=1.6)

card(66, 536, 438, 76, "white", FRONT[1],
     [B("Only in the frontend", 14), R("tokenizer and detokenizer state, per-request output queues,", 12),
      R("request stats and logging. EngineCore never tokenizes.", 12)])
card(66, 628, 438, 92, "white", FRONT[1],
     [B("CoreEngineProcManager", 14), R("created through AsyncMPClient: starts the EngineCore", 12),
      R("process and waits for its startup handshake", 12), NOTE("core_client.py:674 · launch_core_engines", 11)])

# ── column 2: EngineCore process ──────────────────────────────────────────────
column(720, 480, COL_H, CORE, "EngineCore process", "EngineCoreProc", "1 process")
c.text(736, 236, "one Python process, three threads · no model weights or KV-cache tensors", 12, "b", MUTED)
card(736, 252, 224, 74, "white", CORE[1], [B("Input I/O thread", 14), M("ZMQ DEALER", 11), R("decode → input_queue", 12)], "5")
card(736, 342, 224, 74, "white", CORE[1], [B("Output I/O thread", 14), R("output_queue → encode", 12), M("ZMQ PUSH", 11)], "5")
c.cylinder(984, 262, 110, 54, *QUEUE, ry=6)
c.lines(1039, 276, [M("input_queue", 11), NOTE("queue.Queue", 10)], anchor="middle")
c.cylinder(984, 352, 110, 54, *QUEUE, ry=6)
c.lines(1039, 366, [M("output_queue", 11), NOTE("queue.Queue", 10)], anchor="middle")
c.arrow([(960, 289), (982, 289)], LOCAL, sw=1.6)
c.arrow([(1094, 289), (1160, 289), (1160, 452)], LOCAL, sw=1.6)            # input_queue → busy loop
c.arrow([(1039, 454), (1039, 408)], LOCAL, sw=1.6)                          # busy loop → output_queue
c.arrow([(984, 379), (962, 379)], LOCAL, sw=1.6)

c.rect(736, 454, 448, 266, CORE[3], CORE[1], r=10, sw=1.2)
c.text(752, 478, "Busy loop", 16, "b")
c.text(762 + width("Busy loop", "b", 16), 478, "main thread", 13, "r", MUTED)
c.badge(1168, 472, "6", BADGE, r=10, size=11)
c.text(752, 498, "each step: schedule → execute_model → update_from_output", 12, "r", INK)
card(752, 512, 200, 92, "white", CORE[1], [B("Scheduler", 14), R("request queues and", 12), R("KV block allocation", 12),
                                          NOTE("(block ids, not tensors)", 11)])
card(752, 616, 200, 92, "white", CORE[1], [B("Structured outputs", 14), R("grammar manager", 12), R("for constrained", 12),
                                          R("decoding", 12)])
EX_X, EX_W = 968, 200
card(EX_X, 512, EX_W, 196, "white", CORE[1],
     [B("MultiprocExecutor", 14), NOTE("an object here, not a", 11), NOTE("process of its own", 11),
      R("spawns one WorkerProc", 12), R("per GPU; writes the", 12), R("broadcast queue and", 12),
      R("reads every worker's", 12), R("reply queue", 12)], "7")
c.arrow([(952, 560), (966, 560)], LOCAL, sw=1.6)

# ── column 3: worker processes ────────────────────────────────────────────────
column(1480, 520, COL_H, WORK, "Worker processes", "one per TP rank / GPU", "N processes")
WP_X, GW_X, G_X, CW = 1508, 1662, 1816, 140


def worker(y, rank, output_rank=False):
    c.panel(1496, y, 456, 124, WORK[3], WORK[1], "white", band_h=32, r=10, sw=1.4)
    c.text(1510, y + 22, f"Worker process · TP rank {rank}", 14, "b")
    if output_rank:
        c.pill(1938, y + 16, "output rank", "white", NCCL, size=11)
    card(WP_X, y + 40, CW, 74, WORK[3], WORK[1], [B("WorkerProc", 14), R("RPC busy loop", 12), R("replies if asked", 12)])
    card(GW_X, y + 40, CW, 74, WORK[3], WORK[1], [B("GPU Worker", 14), M("GPUModelRunner", 11), R("runs the model", 12)], "9")
    c.rect(G_X, y + 40, 122, 74, *GPU, r=8, sw=1.5)
    c.lines(G_X + 12, y + 44, [B(f"GPU {rank}", 14), R("weights shard", 12), R("KV cache", 12)])
    c.arrow([(WP_X + CW, y + 77), (GW_X - 2, y + 77)], LOCAL, sw=1.6)
    c.arrow([(GW_X + CW, y + 77), (G_X - 2, y + 77)], LOCAL, sw=1.6)
    return y + 54, y + 100, y + 77            # upper port, lower port, row centre


card(1496, 212, 480, 52, "white", WORK[1],
     [R("Model weights (each rank's shard) and the KV cache live only here, in GPU memory.", 12),
      R("Each WorkerProc reads the one broadcast queue and owns one reply queue.", 12)])

r0_up, r0_low, r0_mid = worker(276, "0", True)
r1_up, r1_low, r1_mid = worker(410, "1")
c.text(1510, 551, "⋮  ranks 2 … N−2: same layout", 12, "r", MUTED)
rn_up, rn_low, rn_mid = worker(560, "N−1")

c.rect(1496, 696, 456, 58, "white", NCCL, r=8, sw=1.6)
c.lines(1510, 698, [("TP process group", "b", 13, NCCL), R("NCCL on CUDA: collectives on activations between GPUs of different worker", 12),
                    R("processes; it never goes through EngineCore", 12)])

TP_X = 1978
for y in (r0_mid, r1_mid, rn_mid):
    c.arrow([(G_X + 122, y), (TP_X, y)], NCCL, sw=2.4, head=False)
c.arrow([(TP_X, r0_mid), (TP_X, 725), (1952, 725)], NCCL, sw=2.4, head=False)

# ── gutter 1: frontend ↔ EngineCore ───────────────────────────────────────────
link_card(530, 256, 180, 66, ZMQ, [("ZMQ  ROUTER → DEALER", "b", 12, ZMQ), R("EngineCoreRequest, abort,", 11),
                                    R("utility · msgpack", 11)], badge="4")
c.arrow([(492, 289), (528, 289)], ZMQ, sw=2.4, head=False)
c.arrow([(710, 289), (734, 289)], ZMQ, sw=2.4)
link_card(530, 346, 180, 66, ZMQ, [("ZMQ  PUSH → PULL", "b", 12, ZMQ), R("EngineCoreOutputs", 11), R("msgpack", 11)], badge="4")
c.arrow([(736, 379), (712, 379)], ZMQ, sw=2.4, head=False)
c.arrow([(530, 379), (494, 379)], ZMQ, sw=2.4)
link_card(530, 642, 180, 64, LIFE, [("startup handshake", "b", 12, MUTED), R("HELLO → addresses → READY", 11),
                                     NOTE("core.py:1210-1330", 10)], dash="6 4")
c.arrow([(504, 674), (528, 674)], LIFE, sw=1.8, dash="6 4", head=False)
c.arrow([(710, 674), (718, 674)], LIFE, sw=1.8, dash="6 4")

# ── gutter 2: one broadcast queue out, one reply queue per worker back ─────────
link_card(1234, 216, 232, 56, LIFE, [("multiprocessing pipes", "b", 12, MUTED), R("READY at start · death pipe", 11)], dash="6 4")
c.arrow([(1200, 244), (1232, 244)], LIFE, sw=1.8, dash="6 4", head=False)
c.arrow([(1466, 244), (1478, 244)], LIFE, sw=1.8, dash="6 4")

CYL_X, CYL_W, CYL_H = 1220, 168, 38
QX_R, QX_B = 1396, 1452                     # first reply jog column, broadcast bus
c.text(1304, 518, "shared-memory queues", 12, "b", INK, "middle")
c.badge(1304 - width("shared-memory queues", "b", 12) / 2 - 14, 514, "8", BADGE, r=9, size=10)


def mq(cy, title, sub, color, fill):
    c.cylinder(CYL_X, cy - CYL_H / 2, CYL_W, CYL_H, fill, color, ry=5)
    c.lines(CYL_X + CYL_W / 2, cy - CYL_H / 2 + 5, [(title, "b", 12, INK), (sub, "r", 10, INK)], anchor="middle")
    return cy


q0 = mq(548, "worker_response_mq", "rank 0 · ModelRunnerOutput", REPLY, "#F6EEF8")
q1 = mq(592, "worker_response_mq", "rank 1 · all-rank RPCs", REPLY, "#F6EEF8")
qn = mq(636, "worker_response_mq", "rank N−1 · all-rank RPCs", REPLY, "#F6EEF8")
qb = mq(680, "rpc_broadcast_mq", "1 writer → N readers", BCAST, "#FFF4C2")
c.lines(1304, 716, [NOTE("RPC = (method, args, kwargs, output_rank);", 10), NOTE("execute_model carries the SchedulerOutput", 10)],
        anchor="middle")

EX_R = EX_X + EX_W
c.arrow([(EX_R, qb), (CYL_X - 2, qb)], BCAST, sw=2.6)                                    # executor writes broadcast
c.arrow([(CYL_X + CYL_W, qb), (QX_B, qb), (QX_B, r0_low), (WP_X - 2, r0_low)], BCAST, sw=2.6)
for low in (r1_low, rn_low):
    c.arrow([(QX_B, low), (WP_X - 2, low)], BCAST, sw=2.6)
for i, (up, q) in enumerate([(r0_up, q0), (r1_up, q1), (rn_up, qn)]):            # each worker → its own queue
    jx = QX_R + 14 * i
    c.arrow([(WP_X, up), (jx, up), (jx, q), (CYL_X + CYL_W + 2, q)], REPLY, sw=2.0)
for q in (q0, q1, qn):
    c.arrow([(CYL_X, q), (EX_R + 2, q)], REPLY, sw=2.0)                                   # executor reads each

# ── code anchors (badge = answer-key fact) and key ────────────────────────────
c.rect(24, 802, 1992, 118, "#f6f8fa", "#d0d7de", r=12, sw=1.2)
c.text(44, 826, "Code anchors", 14, "b")
c.text(54 + width("Code anchors", "b", 14), 826, "badge numbers are the answer-key facts; paths under vllm/v1/", 12, "r", MUTED)
ANCHORS = [
    ("1", "engine/async_llm.py:80"), ("2", "async_llm.py:157, 167 · input_processor.py:41 · output_processor.py:51"),
    ("3", "async_llm.py:180 · core_client.py:137-175, 1086"), ("4", "core_client.py:616-662 · core.py:1775, 1878"),
    ("5", "core.py:1088-1199, 1473, 1757-1894"), ("6", "core.py:140, 152, 168, 630-660"),
    ("7", "executor/multiproc_executor.py:111, 195"), ("8", "multiproc_executor.py:164-170, 619, 1032-1036"),
    ("9", "worker/gpu_worker.py:536"),
    ("+", "TP group gpu_worker.py:491, 1586-1624 · output rank multiproc_executor.py:543-557"),
]
for i, (n, ref) in enumerate(ANCHORS):
    col, r = divmod(i, 5)
    x, y = 52 + col * 960, 850 + r * 15
    c.text(x, y, f"[{n}]", 11, "m", BADGE)
    c.text(x + 30, y, ref, 11, "m", INK)

x = 40
for color, dash, label in [(ZMQ, None, "ZMQ socket"), (BCAST, None, "broadcast queue (shared memory, 1 → N)"),
                           (REPLY, None, "reply queue owned by one worker"), (NCCL, None, "NCCL collective"),
                           (LIFE, "6 4", "startup / lifecycle only"), (LOCAL, None, "in-process call or queue")]:
    c.arrow([(x, 948), (x + 36, 948)], color, sw=2.4, dash=dash, head=color != NCCL)
    c.text(x + 46, 953, label, 13)
    x += 46 + width(label, "r", 13) + 36
c.text(2000, 953, "vLLM @ 4c2d277", 12, "m", FAINT, "end")

print(*c.save("a1-process-arch"))
