"""Render out/ppo-step.png: one verl PPO/GRPO step (RayPPOTrainer.fit) as swimlanes.

All line refs are to verl @ fbb4b3a8 (see PINNED.txt). RT = verl/trainer/ppo/ray_trainer.py,
EW = verl/workers/engine_workers.py, CE = verl/checkpoint_engine/base.py, CA = verl/trainer/ppo/core_algos.py.
"""

from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/truetype/dejavu/"
font = lambda name, size: ImageFont.truetype(F + name, size)
FN, FB, FM = font("DejaVuSans.ttf", 15), font("DejaVuSans-Bold.ttf", 15), font("DejaVuSansMono.ttf", 13)
FH, FT, FS = font("DejaVuSans-Bold.ttf", 17), font("DejaVuSans-Bold.ttf", 28), font("DejaVuSans.ttf", 15)
FSTEP = font("DejaVuSans-Bold.ttf", 16)

W = 2620
INK, MUTED, GRID = "#1f2328", "#57606a", "#d0d7de"
WEIGHT = "#d9480f"  # weight movement
LANES = {  # x0, x1, header, fill, border
    "drv": (30, 800, "DRIVER  (single controller process)", "#e7f0fb", "#3b6fb6"),
    "act": (860, 1300, "actor_rollout_wg  (Ray worker group)", "#e6f4ea", "#2f8a4c"),
    "rol": (1360, 1760, "Rollout replicas  (Ray actors)", "#fff4e0", "#c77700"),
    "oth": (1820, 2160, "Other Ray worker groups", "#f1ebfb", "#7048b6"),
    "bat": (2220, 2590, "Batch (DataProto) on driver", "#f6f8fa", "#57606a"),
}
LANE_SUB = {
    "drv": "RayPPOTrainer.fit()  RT L1405 — builds the dataflow by RPC; does advantage itself",
    "act": "ActorRolloutRefWorker: FSDP/Megatron actor + colocated rollout adapter (hybrid_engine, RT L785)",
    "rol": "vLLM / SGLang servers from LLMServerManager (RT L951), driven by AgentLoopManager (RT L960)",
    "oth": "ref_policy_wg · critic_wg · RewardLoopManager (RT L883-919)",
    "bat": "keys accumulated in batch.batch / non_tensor_batch",
}

def wrap(d, text, f, width):
    out = []
    for para in text.split("\n"):
        words, cur = para.split(" "), ""
        for w in words:
            t = (cur + " " + w).strip() if cur else w
            if d.textlength(t, font=f) <= width:
                cur = t
            else:
                if cur:
                    out.append(cur)
                cur = w
        out.append(cur)
    return out

STYLE = {"b": (FB, INK, 21), "n": (FN, INK, 20), "m": (FM, MUTED, 18), "i": (FN, MUTED, 20)}

def layout(d, lines, width):
    """lines: list of (style, text) -> list of (font, color, lh, text)"""
    res = []
    for st, txt in lines:
        f, c, lh = STYLE[st]
        for s in wrap(d, txt, f, width):
            res.append((f, c, lh, s))
    return res

def box_height(d, lines, width):
    return sum(lh for _, _, lh, _ in layout(d, lines, width - 24)) + 20

def draw_box(d, x0, y0, x1, lines, fill, border, h=None, bw=2, dash=False):
    lay = layout(d, lines, x1 - x0 - 24)
    hh = h or sum(l[2] for l in lay) + 20
    d.rounded_rectangle([x0, y0, x1, y0 + hh], radius=10, fill=fill, outline=border, width=bw)
    y = y0 + 10
    for f, c, lh, s in lay:
        d.text((x0 + 12, y), s, font=f, fill=c)
        y += lh
    return hh

def arrow(d, x0, y0, x1, y1, color=INK, width=2, dashed=False, head=11):
    import math
    if dashed:
        L = math.hypot(x1 - x0, y1 - y0)
        n = int(L // 10)
        for i in range(0, n, 2):
            a, b = i / n, min((i + 1) / n, 1)
            d.line([x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b], fill=color, width=width)
    else:
        d.line([x0, y0, x1, y1], fill=color, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    p1 = (x1 - head * math.cos(ang - 0.4), y1 - head * math.sin(ang - 0.4))
    p2 = (x1 - head * math.cos(ang + 0.4), y1 - head * math.sin(ang + 0.4))
    d.polygon([(x1, y1), p1, p2], fill=color)

# ---------------------------------------------------------------- content
# Each step: title, driver lines, {lane: lines}, batch chips, arrows spec
STEPS = [
    dict(
        n="1", t="Prepare prompts",
        drv=[("n", "batch = DataProto.from_single_dict(batch_dict)"), ("m", "RT L1478"),
             ("n", "uid = uuid4() per prompt (GRPO group id)"), ("m", "RT L1482"),
             ("n", "gen_batch = _get_gen_batch(batch); gen_batch.repeat(rollout.n, interleave=True)"),
             ("m", "RT L1486-1491")],
        bat=[("+ prompt tensors from the dataloader", 0), ("+ uid, data_source, reward_model, extra_info", 0)],
    ),
    dict(
        n="2", t="gen — rollout",
        drv=[("n", "async_rollout_manager.generate_sequences(gen_batch)"), ("m", "RT L1513"),
             ("n", "checkpoint_manager.sleep_replicas()"), ("m", "RT L1514")],
        rol=[("b", "generate n responses per prompt"),
             ("n", "replicas already hold θ_k (put there by step 11 of the previous iteration, or RT L1430 before step 1)"),
             ("n", "then sleep(): free weights + KV cache so the trainer can use the GPUs"), ("m", "CE L466-469")],
        oth=[("b", "RewardLoop workers"),
             ("n", "score each finished sample while generation streams (if no RM, or RM has its own pool)"),
             ("m", "RT L949, L959")],
        bat=[("+ responses (+ full-seq input_ids, masks)", 1), ("+ rollout_log_probs (opt.)", 1),
             ("+ rm_scores (if reward streamed)", 1)],
        arrows=[("call", "rol"), ("ret", "rol"), ("stream", "rol", "oth")],
    ),
    dict(
        n="3", t="Merge & balance",
        drv=[("n", "batch = batch.repeat(n, interleave=True).union(gen_batch_output)"), ("m", "RT L1540-1541"),
             ("n", "response_mask = attention_mask[:, -response_len:]"), ("m", "RT L1544, L120-135"),
             ("n", "_balance_batch: reorder so DP ranks get equal token counts"), ("m", "RT L1549-1553")],
        bat=[("+ response_mask", 0), ("meta: global_token_num", 0)],
    ),
    dict(
        n="4", t="reward",
        drv=[("n", "if use_rm and 'rm_scores' not in batch: batch ∪= _compute_reward_colocate(batch)"),
             ("m", "RT L1563-1565, L588-594"),
             ("n", "reward_tensor, extras = extract_reward(batch) — held on the driver until step 8"),
             ("m", "RT L1568")],
        oth=[("b", "RewardLoopManager"), ("n", "compute_rm_score: colocated reward model (only if not already streamed)")],
        bat=[("+ rm_scores (if computed here)", 4)],
        arrows=[("call", "oth"), ("ret", "oth")],
    ),
    dict(
        n="5", t="old log-probs  (π_old)",
        drv=[("n", "_compute_old_log_prob(batch) → actor_rollout_wg.compute_log_prob"), ("m", "RT L1586, L1304"),
             ("n", "entropy → metric actor/entropy, then popped"), ("m", "RT L1587-1601"),
             ("i", "Bypass mode: apply_bypass_mode sets old_log_probs = rollout_log_probs — no RPC (RT L1576-1583)")],
        act=[("b", "compute_log_prob"), ("n", "actor.infer_batch: forward-only with the current weights θ_k"),
             ("m", "EW L700-706")],
        bat=[("+ old_log_probs", 5), ("(+ routed_experts / sum_pi_squared, opt.)", 5)],
        arrows=[("call", "act"), ("ret", "act")],
    ),
    dict(
        n="6", t="ref log-probs  (π_ref)",
        cond="if use_reference_policy",
        drv=[("n", "_compute_ref_log_prob(batch)"), ("m", "RT L1621, L1266-1288"),
             ("n", "→ ref_policy_wg.compute_ref_log_prob, or actor_rollout_wg.compute_log_prob(no_lora_adapter) when ref_in_actor (LoRA)"),
             ("m", "RT L1276-1279")],
        oth=[("b", "ref_policy_wg"), ("n", "ref.infer_batch with the frozen reference model"), ("m", "EW L693-698")],
        bat=[("+ ref_log_prob", 6)],
        arrows=[("call", "oth"), ("ret", "oth")],
    ),
    dict(
        n="7", t="values  V(s)",
        cond="if use_critic (e.g. GAE)",
        drv=[("n", "_compute_values(batch) → critic_wg.infer_batch"), ("m", "RT L1627, L1252-1264")],
        oth=[("b", "critic_wg"), ("n", "value model forward-only"), ("m", "EW L397-398")],
        bat=[("+ values", 7)],
        arrows=[("call", "oth"), ("ret", "oth")],
    ),
    dict(
        n="8", t="adv — runs ON THE DRIVER",
        drv=[("n", "token_level_scores = reward_tensor  (+ reward extras into non_tensor_batch)"), ("m", "RT L1633-1636"),
             ("n", "use_kl_in_reward ? apply_kl_penalty: rewards = scores − β·KL(old_log_probs, ref_log_prob), β adapted"),
             ("m", "RT L1639-1643, L78-117"),
             ("n", "otherwise token_level_rewards = token_level_scores"), ("m", "RT L1645"),
             ("n", "rollout-correction IS weights (optional, decoupled mode)"), ("m", "RT L1650-1660"),
             ("n", "compute_advantage: GAE(rewards, values, γ, λ) | GRPO: per-uid (score − mean)/std | other estimators"),
             ("m", "RT L1667, L187-282; CA L216, L268-331")],
        bat=[("+ token_level_scores", 8), ("+ token_level_rewards", 8), ("+ advantages, returns", 8),
             ("(+ rollout_is_weights, opt.)", 8)],
    ),
    dict(
        n="9", t="update critic",
        cond="if use_critic",
        drv=[("n", "_update_critic(batch) → critic_wg.train_mini_batch"), ("m", "RT L1679, L1378-1403"),
             ("n", "mini-batch = critic.ppo_mini_batch_size·n, critic.ppo_epochs")],
        oth=[("b", "critic_wg"), ("n", "value_loss (set_loss_fn, RT L891) on values vs returns; optimizer steps"),
             ("m", "EW L242-243")],
        bat=[("returns metrics only", 9)],
        arrows=[("call", "oth"), ("ret", "oth")],
    ),
    dict(
        n="10", t="update actor",
        cond="skipped while critic_warmup > global_steps (RT L1684-1686: only re-sync weights)",
        drv=[("n", "_update_actor(batch) → actor_rollout_wg.update_actor"), ("m", "RT L1690, L1327-1376"),
             ("n", "mini-batch = actor.ppo_mini_batch_size·n, actor.ppo_epochs"),
             ("n", "then _save_checkpoint() if save_freq hit"), ("m", "RT L1704-1712")],
        act=[("b", "update_actor"), ("n", "actor.train_mini_batch: policy loss on advantages vs old_log_probs; θ_k → θ_k+1"),
             ("m", "EW L708-715")],
        bat=[("returns metrics only", 9)],
        arrows=[("call", "act"), ("ret", "act")],
    ),
    dict(
        n="11", t="update_weights  trainer → rollout",
        drv=[("n", "checkpoint_manager.update_weights(global_steps)"), ("m", "RT L1716;  CE L509-562"),
             ("i", "same call: before step 1 (RT L1430) and during critic warmup (RT L1686)")],
        act=[("b", "update_weights(mode=backend)"), ("m", "EW L727-827"),
             ("n", "naive (colocated): rollout.resume(weights) → get_per_tensor_param() → rollout.update_weights in-process → offload actor → rollout.resume(kv_cache)"),
             ("n", "other backends: get_per_tensor_param() → checkpoint_engine.send_weights")],
        rol=[("b", "replicas wake up holding θ_k+1"),
             ("n", "non-naive: abort → release KV → build_process_group → receive_weights (NCCL/NIXL…) → finalize → resume"),
             ("m", "CE L522-560, L354-360")],
        bat=[("— (no batch traffic)", 9)],
        arrows=[("call", "act"), ("weights", "act", "rol")],
    ),
    dict(
        n="12", t="Validate, metrics, log",
        drv=[("n", "_validate() if test_freq hit"), ("m", "RT L1727-1734"),
             ("n", "data / timing / throughput metrics; logger.log; global_steps += 1"), ("m", "RT L1772-1806")],
        bat=[],
    ),
]

CHIP = ["#dbe7f7", "#ffe8c2", "", "", "#ece2fb", "#d3f0dc", "#e7dcf8", "#e2d6f6", "#cfe2fa", "#eeeeee"]

# ---------------------------------------------------------------- measure
scratch = ImageDraw.Draw(Image.new("RGB", (10, 10)))
TOP = 300
ROWPAD = 18
rows = []
y = TOP
for s in STEPS:
    hs = []
    x0, x1 = LANES["drv"][:2]
    hdr = 30 + (22 if s.get("cond") else 0)
    hs.append(hdr + box_height(scratch, s["drv"], x1 - x0 - 60))
    for ln in ("act", "rol", "oth"):
        if ln in s:
            a, b = LANES[ln][:2]
            hs.append(hdr + box_height(scratch, s[ln], b - a))
    hs.append(hdr + 30 * max(1, len(s["bat"])) + 10)
    h = max(hs) + ROWPAD
    rows.append((y, h))
    y += h
H = y + 220

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- header
d.text((30, 22), "verl — what one PPO / GRPO training step does  (RayPPOTrainer.fit, single-controller)", font=FT, fill=INK)
d.text((30, 64), "verl @ fbb4b3a8bf63 (2026-09-30).  RT = verl/trainer/ppo/ray_trainer.py   EW = verl/workers/engine_workers.py   "
       "CE = verl/checkpoint_engine/base.py   CA = verl/trainer/ppo/core_algos.py", font=FS, fill=MUTED)
d.text((30, 88), "Note: RayPPOTrainer is marked @deprecated at this commit (RT L285: legacy trainer, use trainer.use_v1=True); "
       "this is still the loop in the pinned file.", font=FS, fill=MUTED)

# legend
lx, ly = 30, 124
d.rounded_rectangle([lx, ly, lx + 2560, ly + 60], radius=8, outline=GRID, width=1, fill="#fbfcfd")
arrow(d, lx + 20, ly + 20, lx + 90, ly + 20)
d.text((lx + 100, ly + 11), "RPC from the driver into a worker group", font=FN, fill=INK)
arrow(d, lx + 510, ly + 20, lx + 440, ly + 20, color=MUTED, dashed=True)
d.text((lx + 525, ly + 11), "result returned & union-ed into the batch", font=FN, fill=INK)
arrow(d, lx + 900, ly + 20, lx + 970, ly + 20, color=WEIGHT, width=6, head=16)
d.text((lx + 985, ly + 11), "model weights move (trainer → rollout engine)", font=FB, fill=WEIGHT)
arrow(d, lx + 1440, ly + 20, lx + 1510, ly + 20, color="#c77700", dashed=True)
d.text((lx + 1525, ly + 11), "samples streamed to the reward loop", font=FN, fill=INK)
d.text((lx + 20, ly + 36),
       "Each RPC: driver does batch.to_tensordict() + left_right_2_no_padding, the worker group's dispatch fn "
       "(make_nd_compute_dataproto_dispatch_fn, EW) shards it across DP ranks and gathers outputs, "
       "and the driver restores padding (no_padding_2_padding).",
       font=FM, fill=MUTED)

# lane headers + backgrounds
for key, (x0, x1, title, fill, border) in LANES.items():
    d.rectangle([x0 - 10, 200, x1 + 10, H - 200], fill="#fcfcfd" if key != "drv" else "#f7faff", outline=GRID)
    d.rectangle([x0 - 10, 200, x1 + 10, 286], fill=fill, outline=border, width=2)
    d.text((x0, 208), title, font=FH, fill=border)
    yy = 234
    for s in wrap(d, LANE_SUB[key], FM, x1 - x0):
        d.text((x0, yy), s, font=FM, fill=INK)
        yy += 17

# GPU-sharing bracket between actor and rollout lanes
d.text((870, H - 192), "actor_rollout_wg and the rollout replicas share the same resource pool / GPUs "
       "(hybrid engine, RT L785-793, L951-953): that is why rollout sleeps after gen (step 2) and only wakes "
       "when weights are pushed (step 11).", font=FN, fill="#c77700")

# ---------------------------------------------------------------- rows
for i, (s, (ry, rh)) in enumerate(zip(STEPS, rows)):
    if i % 2 == 0:
        d.rectangle([20, ry, W - 20, ry + rh - 4], fill=None, outline=None)
    d.line([20, ry + rh - 6, W - 20, ry + rh - 6], fill=GRID, width=1)
    dx0, dx1 = LANES["drv"][:2]
    # step badge + title
    d.ellipse([dx0, ry + 6, dx0 + 34, ry + 40], fill="#3b6fb6")
    tw = d.textlength(s["n"], font=FSTEP)
    d.text((dx0 + 17 - tw / 2, ry + 13), s["n"], font=FSTEP, fill="white")
    d.text((dx0 + 46, ry + 12), s["t"], font=FH, fill=INK)
    hdr = 30
    if s.get("cond"):
        d.text((dx0 + 46, ry + 36), s["cond"], font=FN, fill="#9a6700")
        hdr += 22
    by = ry + hdr + 14
    is_adv = s["n"] == "8"
    boxes = {}
    h = draw_box(d, dx0 + 46, by, dx1, s["drv"], "#fff7d6" if is_adv else LANES["drv"][3],
                 "#b08800" if is_adv else LANES["drv"][4], bw=3 if is_adv else 2)
    boxes["drv"] = (dx0 + 46, by, dx1, by + h)
    for ln in ("act", "rol", "oth"):
        if ln in s:
            a, b, _, fill, border = LANES[ln]
            hh = draw_box(d, a, by, b, s[ln], fill, border, bw=3 if s["n"] == "11" and ln != "oth" else 2)
            boxes[ln] = (a, by, b, by + hh)
    # arrows
    for ar in s.get("arrows", []):
        kind = ar[0]
        if kind == "call":
            tgt = boxes[ar[1]]
            arrow(d, boxes["drv"][2], by + 20, tgt[0], by + 20)
        elif kind == "ret":
            tgt = boxes[ar[1]]
            arrow(d, tgt[0], by + 44, boxes["drv"][2], by + 44, color=MUTED, dashed=True)
        elif kind == "stream":
            a, b = boxes[ar[1]], boxes[ar[2]]
            yy = by + 40
            arrow(d, a[2], yy, b[0], yy, color="#c77700", dashed=True)
        elif kind == "weights":
            a, b = boxes[ar[1]], boxes[ar[2]]
            yy = by + 34
            arrow(d, a[2] + 2, yy, b[0] - 2, yy, color=WEIGHT, width=8, head=20)
            d.text((a[2] + 6, yy + 12), "θ_k+1", font=FB, fill=WEIGHT)
    # batch chips
    bx0, bx1 = LANES["bat"][:2]
    cy = by
    for txt, ci in s["bat"]:
        meta = txt.startswith(("meta", "(", "returns", "—"))
        if meta:
            d.text((bx0 + 4, cy + 5), txt, font=FM, fill=MUTED)
        else:
            col = CHIP[ci] or "#dbe7f7"
            tw = d.textlength(txt, font=FM)
            d.rounded_rectangle([bx0, cy, min(bx0 + tw + 18, bx1), cy + 24], radius=6, fill=col, outline="#8c959f")
            d.text((bx0 + 9, cy + 4), txt, font=FM, fill=INK)
        cy += 30

# weight-sync callout at first rollout row: the rollout holds θ_k on entry
r2y = rows[1][0]
# loop-back arrow on the far left: step 12 -> step 1
ly0 = rows[0][0] + 22
ly1 = rows[-1][0] + 22
d.line([16, ly1, 8, ly1, 8, ly0, 16, ly0], fill="#3b6fb6", width=3)
arrow(d, 8, ly0, 30, ly0, color="#3b6fb6", width=3)

# footer
fy = H - 160
d.text((30, fy), "Reading the flow", font=FH, fill=INK)
notes = [
    "• The driver runs steps 1, 3, 8 and 12 itself (data prep, merge/balance, KL-in-reward and advantage). Every other step is a blocking RPC into a Ray "
    "worker group, so steps run strictly in order 2 → 11.",
    "• GRPO (critic off): steps 7 and 9 are skipped and the advantage is group-normalized per uid. PPO with GAE: the critic gives values (7) and is trained on returns (9) before the actor (10).",
    "• Weights move once per step, at 11: from the actor's training engine (FSDP/Megatron) to the rollout engine (vLLM/SGLang). Everything else moves the batch (DataProto ⇄ TensorDict).",
]
yy = fy + 28
for n_ in notes:
    for s_ in wrap(d, n_, FN, W - 80):
        d.text((30, yy), s_, font=FN, fill=INK)
        yy += 21

img.save("/tmp/claude-eval-zznZLQ/home/cwd/out/ppo-step.png")
print(img.size)
