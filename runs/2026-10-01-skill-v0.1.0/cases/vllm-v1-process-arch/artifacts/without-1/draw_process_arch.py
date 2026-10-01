"""Hand-laid-out process architecture diagram for vLLM V1 (single node, TP, MultiprocExecutor).

All file:line citations refer to vllm@4c2d277643e2 (see PINNED.txt in the source dir).
Run: python3 draw_process_arch.py  ->  process-arch.png next to this script.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 3960, 1960
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

FD = "/usr/share/fonts/truetype/dejavu/"
F = lambda s, b=False: ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if b else "DejaVuSans.ttf"), s)
MONO = ImageFont.truetype(FD + "DejaVuSansMono.ttf", 14)
T_BIG, T_PROC, T_BOX, T_BODY, T_SMALL = F(34, True), F(22, True), F(17, True), F(15), F(13)
T_LBL_B, T_LBL = F(15, True), F(14)

BLUE, BLUE_BG, BLUE_IN = "#2F5D9A", "#E8F0FB", "#D3E2F6"
ORANGE, ORANGE_BG, ORANGE_IN = "#B5651D", "#FDF1E4", "#FADDBF"
GREEN, GREEN_BG, GREEN_IN = "#3C7A3C", "#E7F4E7", "#C9E6C9"
PURPLE, GREY, DARK = "#8B1E8B", "#7A7A7A", "#222222"

overflow = []


def check(text, font, maxw, where):
    if d.textlength(text, font=font) > maxw:
        overflow.append(f"{where}: '{text[:50]}' {d.textlength(text, font=font):.0f}>{maxw}")


def container(x0, y0, x1, y1, title, sub, color, bg, width=4, dash=False):
    if dash:
        dashed_rect(x0, y0, x1, y1, color, 3)
    else:
        d.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=bg, outline=color, width=width)
    d.text((x0 + 18, y0 + 10), title, font=T_PROC, fill=color)
    for i, s in enumerate(sub):
        check(s, T_SMALL, x1 - x0 - 30, title)
        d.text((x0 + 18, y0 + 40 + i * 17), s, font=T_SMALL, fill=DARK)


def box(x0, y0, x1, y1, title, lines, fill="white", outline="#555555", width=2, tfont=None):
    d.rounded_rectangle((x0, y0, x1, y1), radius=10, fill=fill, outline=outline, width=width)
    tfont = tfont or T_BOX
    check(title, tfont, x1 - x0 - 24, title)
    d.text((x0 + 12, y0 + 8), title, font=tfont, fill=DARK)
    y = y0 + 8 + 24
    for s in lines:
        font = T_BODY
        if isinstance(s, tuple):
            s, font = s
        check(s, font, x1 - x0 - 24, title)
        d.text((x0 + 12, y), s, font=font, fill=DARK)
        y += 20
    if y > y1 - 2:
        overflow.append(f"{title}: text bottom {y} > {y1}")


def dashed_line(p, q, color, width, dash=12, gap=8):
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0)
    if L == 0:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    t = 0
    while t < L:
        e = min(t + dash, L)
        d.line((x0 + ux * t, y0 + uy * t, x0 + ux * e, y0 + uy * e), fill=color, width=width)
        t = e + gap


def dashed_rect(x0, y0, x1, y1, color, width):
    for p, q in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
        dashed_line(p, q, color, width)


def head(p, q, color, size=16):
    (x0, y0), (x1, y1) = p, q
    a = math.atan2(y1 - y0, x1 - x0)
    pts = [(x1, y1),
           (x1 - size * math.cos(a - 0.4), y1 - size * math.sin(a - 0.4)),
           (x1 - size * math.cos(a + 0.4), y1 - size * math.sin(a + 0.4))]
    d.polygon(pts, fill=color)


def path(pts, color, width=4, dashed=False, start=False, end=True):
    for p, q in zip(pts, pts[1:]):
        (dashed_line if dashed else lambda a, b, c, w: d.line((*a, *b), fill=c, width=w))(p, q, color, width)
    if end:
        head(pts[-2], pts[-1], color, 14 + width * 2)
    if start:
        head(pts[1], pts[0], color, 14 + width * 2)


def label(x, y, lines, color=DARK, maxw=None):
    for i, s in enumerate(lines):
        font = T_LBL
        if isinstance(s, tuple):
            s, font = s
        if maxw:
            check(s, font, maxw, "label")
        d.text((x, y + i * 19), s, font=font, fill=color)


# ---------------------------------------------------------------- title
d.text((40, 30), "vLLM V1 — process architecture: one node, tensor parallel (TP = N), MultiprocExecutor",
       font=T_BIG, fill=DARK)
d.text((40, 78), "Structure only (not step order). Every element is cited as file:line in vllm @ 4c2d277643e2 "
       "(vllm/v1/...). Thick-bordered boxes = OS processes; inner boxes = objects / threads inside that process.",
       font=T_BODY, fill=DARK)
d.text((40, 100), "DP = 1, PP = 1: no DP coordinator process and no TCP between nodes.  "
       "Process tree: frontend → spawns EngineCore → spawns N workers.",
       font=T_BODY, fill=DARK)

# ================================================================ PROCESS 1: FRONTEND
P1 = (40, 150, 900, 1650)
container(*P1, "Process 1 — Frontend (API server) process", [
    "Hosts AsyncLLM, called by the HTTP API server (vllm/entrypoints, not vendored).",
    "AsyncMPClient starts Process 2 via launch_core_engines* (core_client.py:674).",
], BLUE, BLUE_BG)

# AsyncLLM owns everything below (async_llm.py:154-205)
d.rounded_rectangle((60, 226, 880, 1330), radius=14, fill="#F4F8FD", outline=BLUE, width=2)
d.text((76, 231), "AsyncLLM  (async_llm.py:80) — asyncio event loop", font=T_BOX, fill=BLUE)

box(80, 262, 860, 795, "AsyncMPClient  =  AsyncLLM.engine_core  (core_client.py:1086, 180)", [
    ("ZMQ context  (core_client.py:589)", T_LBL_B),
    "input_socket : ZMQ ROUTER, bind  (core_client.py:654)  ──►  to Process 2",
    "   sends ADD / ABORT / UTILITY  (core_client.py:1227, 1278, 1283, 1265)",
    "MsgpackEncoder / MsgpackDecoder(EngineCoreOutputs)  (core_client.py:705-706)",
    "",
    ("Background pieces", T_LBL_B),
    "EngineCoreOutputQueueTask: recv → decode → outputs_queue",
    "   (asyncio task, core_client.py:1151-1205)",
    "MPClientEngineMonitor thread: engine_manager.monitor_engine_liveness()",
    "   marks engine dead if Process 2 exits  (core_client.py:803-819)",
    "engine_manager = CoreEngineProcManager*  (core_client.py:678)",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "output_socket : ZMQ PULL  (core_client.py:661)  ◄──  from Process 2",
], fill=BLUE_IN, outline=BLUE)

box(80, 815, 860, 920, "Renderer + InputProcessor  (async_llm.py:154-157)", [
    "tokenize / validate prompt  →  EngineCoreRequest",
    "process_inputs  (input_processor.py:339)",
])
box(80, 935, 860, 1065, "OutputProcessor  (async_llm.py:167, output_processor.py:469)", [
    "EngineCoreOutputs → RequestOutput: detokenize, stop strings, logprobs",
    "per-request RequestOutputCollector queues  (output_processor.py:51)",
    "process_outputs  (output_processor.py:646)",
])
box(80, 1080, 860, 1210, "output_handler task  (async_llm.py:813-874)", [
    "engine_core.get_output_async() → output_processor.process_outputs()",
    "→ abort reqs finished by stop strings → logger record",
    "",
])
box(80, 1225, 860, 1310, "StatLoggerManager  (async_llm.py:193)", [
    "only when log_stats; records scheduler + iteration stats",
])

box(80, 1420, 860, 1530, "launch_core_engines* — engine handshake socket", [
    "startup only, during AsyncMPClient.__init__  (core_client.py:674-689)",
    "then waits for READY on input_socket  (core_client.py:727-745)",
], fill="#F1F1F1", outline=GREY)

# ================================================================ PROCESS 2: ENGINE CORE
P2 = (1340, 150, 2200, 1650)
container(*P2, "Process 2 — EngineCore process", [
    "Entry: EngineCoreProc.run_engine_core (core.py:1351).",
    "Spawns the N worker processes (multiproc_executor.py:189-204).",
], ORANGE, ORANGE_BG)
d.rounded_rectangle((1360, 226, 2180, 1630), radius=14, fill="#FEF8F1", outline=ORANGE, width=2)
d.text((1376, 231), "EngineCoreProc(EngineCore)  (core.py:1088, 111)", font=T_BOX, fill=ORANGE)

box(1380, 262, 2160, 355, "Input IO thread — process_input_sockets  (core.py:1757)", [
    "ZMQ DEALER, connect, identity = engine_index  (core.py:1775, 1114)",
    "MsgpackDecoder → input_queue  (+ aborts_queue for ABORT)  (core.py:1854-1857)",
], fill=ORANGE_IN, outline=ORANGE)

box(1380, 400, 2160, 650, "Main thread — busy loop  run_busy_loop → step()  (core.py:1473, 630)", [
    "Scheduler (+ KV cache manager)  (core.py:155-176)",
    "   schedule() → SchedulerOutput;  update_from_output() → EngineCoreOutputs",
    "StructuredOutputManager  (core.py:152) → grammar bitmask",
    "mm_receiver_cache  (core.py:187)",
    "batch_queue — only if max_concurrent_batches > 1  (core.py:214-220)",
    "input_queue / output_queue: queue.Queue  (core.py:1107-1108)",
    "",
], fill="white", outline=ORANGE)

box(1380, 700, 1900, 790, "Output IO thread  (core.py:1859)", [
    "output_queue → MsgpackEncoder",
    "→ ZMQ PUSH  (core.py:1878)",
], fill=ORANGE_IN, outline=ORANGE)

box(1380, 860, 2160, 1135, "MultiprocExecutor = model_executor  (core.py:140)", [
    "collective_rpc → FutureWrapper  (multiproc_executor.py:377-450)",
    "execute_model / sample_tokens  (multiproc_executor.py:340-364)",
    "",
    "WRITER: rpc_broadcast_mq = MessageQueue(world_size,",
    "        local_world_size)  (multiproc_executor.py:164)",
    "READER: response_mqs[0 .. N-1]  (multiproc_executor.py:226-239)",
    "parent ends of pipes: ready_reader, death_writer  (:757)",
    "",
    "",
], fill=ORANGE_IN, outline=ORANGE)

box(1380, 1240, 2160, 1355, "MultiprocWorkerMonitor thread  (multiproc_executor.py:305-329)", [
    "waits on worker proc.sentinel; on death → executor shutdown →",
    "failure callback puts EXECUTOR_FAILED on input_queue  (core.py:1109)",
], fill="#F1F1F1", outline=GREY)

box(1380, 1420, 2160, 1530, "Handshake socket — ZMQ DEALER  (core.py:1284-1310)", [
    "startup only: HELLO → receives EngineZmqAddresses → READY",
    "(startup_handshake, core.py:1313-1348)",
], fill="#F1F1F1", outline=GREY)

# internal arrows in Process 2
path([(1500, 355), (1500, 400)], ORANGE, 3)
label(1512, 362, [("input_queue", T_SMALL)])
path([(1500, 650), (1500, 700)], ORANGE, 3)
label(1512, 660, [("output_queue", T_SMALL)])
path([(2140, 650), (2140, 860)], ORANGE, 3)
label(1910, 700, [("execute_model(SchedulerOutput)", T_SMALL), ("sample_tokens(GrammarOutput)", T_SMALL),
                  ("→ Future[ModelRunnerOutput]", T_SMALL)])

# ================================================================ PROCESSES 3..: WORKERS
WX0, WX1 = 2760, 3460
container(2740, 150, 3480, 1650, "Processes 3 … N+2 — GPU workers", [
    "one per TP rank: context.Process(target=WorkerProc.worker_main,",
    "name=f\"VllmWorker-{rank}\")  (multiproc_executor.py:739-750)",
], GREEN, "white", dash=True)


def worker(y0, y1, title, loop_y, gpu_y, thr_y, rank0):
    d.rounded_rectangle((WX0, y0, WX1, y1), radius=16, fill=GREEN_BG, outline=GREEN, width=4)
    d.text((WX0 + 16, y0 + 10), title, font=T_PROC, fill=GREEN)
    box(WX0 + 20, loop_y, WX1 - 20, loop_y + 200, "WorkerProc — worker_busy_loop  (:1032)", [
        "WRITER: worker_response_mq = MessageQueue(1, 1)  (:619)",
        "   enqueue((ResponseStatus, output))  (:986-1003)",
        "",
        "",
        "READER: rpc_broadcast_mq.dequeue() → getattr(worker,",
        "   method)(*args)  (:614, 1036-1050)",
        "replies only if output_rank is None or == rank  (:1052)",
    ], fill="white", outline=GREEN)
    box(WX0 + 20, gpu_y, WX1 - 20, gpu_y + 110, "Worker → GPUModelRunner  (gpu_worker.py:187, 536)", [
        "weight shard + KV cache on cuda:<local_rank>  (gpu_worker.py:482)",
        ("is_driver_worker = rank % TP == 0  (multiproc_executor.py:296)" if rank0 else
         "init_device(): joins TP process group  (gpu_worker.py:491)", T_BODY),
    ], fill=GREEN_IN, outline=GREEN)
    box(WX0 + 20, thr_y, WX1 - 20, thr_y + 82, "Helper threads", [
        "DeathPipeMonitor (:847);  WorkerAsyncOutputCopy",
        "   — only if async_scheduling (:686-693)",
    ], fill="#F1F1F1", outline=GREY, tfont=F(15, True))


# rank 0: response exits at y=290, broadcast enters at y=400
worker(222, 735, "VllmWorker-0  (TP rank 0 = output_rank)", 270, 490, 618, True)
d.text((2990, 790), "⋮   ranks 1 … N-2: identical", font=T_BOX, fill=GREEN)
# rank N-1: broadcast enters at y=1000 (inside loop box), response exits at y=1100
worker(880, 1370, "VllmWorker-(N-1)  (TP rank N-1)", 930, 1150, 1275, False)
# (geometry check below keeps arrows inside the boxes)

# ================================================================ INTER-PROCESS LINKS
# --- frontend -> engine: ZMQ ROUTER -> DEALER
path([(860, 300), (1380, 300)], BLUE, 5)
label(912, 318, [
    ("ZMQ  ROUTER → DEALER", T_LBL_B),
    "local socket from get_engine_zmq_addresses*",
    "multipart [EngineCoreRequestType,",
    "            msgpack frames]:",
    "• ADD  EngineCoreRequest",
    "• ABORT  list of request ids",
    "• UTILITY (client_idx, call_id, method, args)",
    ("reverse direction, startup: engine READY", T_SMALL),
    ("payload (core.py:1797-1803)", T_SMALL),
], BLUE, maxw=425)

# --- engine -> frontend: ZMQ PUSH -> PULL
path([(1380, 745), (860, 745)], BLUE, 5)
label(912, 565, [
    ("ZMQ  PUSH → PULL", T_LBL_B),
    "msgpack EngineCoreOutputs:",
    "per-request new token ids, finish reason,",
    "logprobs; scheduler_stats; utility results;",
    "ENGINE_CORE_DEAD sentinel (core.py:1895)",
], BLUE, maxw=425)

# --- startup handshake
path([(1380, 1475), (860, 1475)], GREY, 3, dashed=True, start=True)
label(912, 1490, [
    ("ZMQ DEALER ↔ handshake socket*", T_LBL_B),
    "startup only: HELLO / addresses / READY",
    "(core.py:1274-1348)",
], GREY, maxw=425)

# --- worker-0 response: (2780,290) -> x=2240 -> y=900 -> executor
path([(WX0 + 20, 290), (2240, 290), (2240, 900), (2160, 900)], GREEN, 5)
label(2252, 172, [
    ("worker_response_mq  (shared memory)", T_LBL_B),
    "MessageQueue(1,1) per worker, one reader",
    "(ResponseStatus, ModelRunnerOutput)",
    "for execute_model / sample_tokens only",
], GREEN, maxw=480)
label(2318, 300, [
    ("output_rank = world_size − TP·PCP = 0", T_SMALL),
    ("replies  (multiproc_executor.py:543-557)", T_SMALL),
], GREEN, maxw=500)

# --- broadcast: executor (2160,1000) -> x=2300 -> up to 400 -> worker0 ; down -> workerN at 1000?
BX = 2300
path([(2160, 1000), (BX, 1000), (BX, 410), (WX0 + 20, 410)], ORANGE, 5)
path([(BX, 1000), (BX, 1000), (WX0 + 20, 1000)], ORANGE, 5)
d.ellipse((BX - 8, 992, BX + 8, 1008), fill=ORANGE)
label(2318, 440, [
    ("rpc_broadcast_mq  (shared memory)", T_LBL_B),
    "shm_broadcast.MessageQueue: ring buffer",
    "in /dev/shm, 1 writer → all N local",
    "readers  (multiproc_executor.py:164)",
    "",
    "(method, args, kwargs, output_rank)",
    "e.g. execute_model(SchedulerOutput),",
    "sample_tokens(GrammarOutput),",
    "or cloudpickled callables (:418-422)",
    "",
    ("every rank receives every RPC", T_SMALL),
], ORANGE, maxw=430)

# --- worker N-1 response (dashed: only for all-rank collective_rpc)
path([(WX0 + 20, 1100), (2160, 1100)], GREEN, 3, dashed=True)
label(2252, 1108, [
    ("its worker_response_mq: read only by", T_SMALL),
    ("collective_rpc with output_rank=None", T_SMALL),
    ("(e.g. check_health, :539)", T_SMALL),
], GREEN, maxw=500)

# --- pipes + liveness (EngineCore <-> every worker)
path([(2160, 1300), (WX0 + 20, 1300)], GREY, 3, dashed=True, start=True)
label(2215, 1305, [
    ("multiprocessing.Pipe ×2 per worker", T_LBL_B),
    "ready_pipe: READY + response-MQ handle  (:719, 923)",
    "death_pipe: EOF when parent dies → worker",
    "   shuts its MQs  (:721, 829-852)",
    "+ proc.sentinel watched by WorkerMonitor",
], GREY, maxw=540)

# --- TP group between workers (GPU <-> GPU)
NX = WX1 + 0
path([(WX1 - 20, 545), (3530, 545), (3530, 1205), (WX1 - 20, 1205)], PURPLE, 6, start=True)
label(3552, 600, [
    ("torch.distributed TP group", T_LBL_B),
    "init_worker_distributed_environment",
    "(gpu_worker.py:491, 1586-1624)",
    "backend = current_platform.dist_backend",
    "(NCCL on CUDA) + custom all-reduce",
    "(gpu_worker.py:1602)",
    "",
    "GPU ↔ GPU collectives (all-reduce /",
    "all-gather of activations) inside",
    "the model forward — between ALL",
    "N workers, not via Process 2",
], PURPLE, maxw=400)

# ================================================================ LEGEND
LY = 1690
d.rounded_rectangle((40, LY, 3920, 1930), radius=12, outline="#999999", width=2)
d.text((60, LY + 12), "Legend", font=T_BOX, fill=DARK)
items = [
    (BLUE, False, "ZMQ socket between frontend and EngineCore (msgpack-serialized; per-request data path)"),
    (ORANGE, False, "shared-memory broadcast MessageQueue, EngineCore → every worker (scheduler work, RPCs)"),
    (GREEN, False, "shared-memory response MessageQueue, worker → EngineCore (ModelRunnerOutput)"),
    (GREEN, True, "same response MQ on ranks ≠ output_rank — idle on the per-step path"),
    (PURPLE, False, "torch.distributed / NCCL process group among GPU workers (tensor-parallel collectives)"),
    (GREY, True, "startup handshake, readiness / death pipes, liveness monitoring (control, not request data)"),
]
for i, (c, dsh, txt) in enumerate(items):
    col, row = i // 3, i % 3
    x, y = 60 + col * 1900, LY + 50 + row * 30
    path([(x, y + 9), (x + 90, y + 9)], c, 4, dashed=dsh)
    d.text((x + 110, y), txt, font=T_BODY, fill=DARK)
d.text((60, LY + 150), "* launch_core_engines, CoreEngineProcManager, get_engine_zmq_addresses and the frontend-side "
       "handshake socket live in vllm/v1/engine/utils.py, which is not in the vendored file set; only their call "
       "sites (cited) were checked.", font=T_SMALL, fill=DARK)
d.text((60, LY + 170), "Optional, not drawn: torch_shm tensor_queue for multimodal tensors (core_client.py:697-703, "
       "core.py:1118-1121); DP coordinator ZMQ sockets (DP > 1 only, core.py:1780-1793, 1882-1890).",
       font=T_SMALL, fill=DARK)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "process-arch.png")
img.save(out)
print("saved", out)
for o in overflow:
    print("OVERFLOW", o)
