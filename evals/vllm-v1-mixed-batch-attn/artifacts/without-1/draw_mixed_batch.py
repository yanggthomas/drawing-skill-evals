"""Draws out/mixed-batch-attn.png: how vLLM V1 (commit 4c2d2776) turns one mixed
prefill/decode batch into FlashAttention inputs. Every value below is computed with
the same formulas as the source so the picture stays consistent with the code."""

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

S = 2  # supersampling factor
W, H = 1820, 1630
FD = "/usr/share/fonts/truetype/dejavu/"


def F(size, bold=False, mono=False):
    name = "DejaVuSansMono" if mono else "DejaVuSans"
    if bold:
        name += "-Bold"
    return ImageFont.truetype(FD + name + ".ttf", int(size * S))


img = Image.new("RGB", (W * S, H * S), "white")
d = ImageDraw.Draw(img)

INK = "#1f2933"
MUTED = "#5f6b7a"
LINE = "#c9d1db"
PANEL = "#f7f9fb"
CODE = "#7a3e9d"

# Per-request colors (base, tint).
COL = {
    0: ("#3b6fb6", "#dbe7f6"),  # A
    1: ("#d9730d", "#fbe5cf"),  # B
    2: ("#3d8b40", "#dcefdc"),  # C
    3: ("#8e5ba8", "#ecdff3"),  # D
}
NAMES = "ABCD"


def R(x, y, w, h, fill=None, outline=None, width=1, r=0):
    box = [x * S, y * S, (x + w) * S, (y + h) * S]
    if r:
        d.rounded_rectangle(box, radius=r * S, fill=fill, outline=outline, width=width * S)
    else:
        d.rectangle(box, fill=fill, outline=outline, width=width * S)


def T(x, y, s, font, fill=INK, anchor="la"):
    d.text((x * S, y * S), s, font=font, fill=fill, anchor=anchor)


def L(x1, y1, x2, y2, fill=INK, width=1):
    d.line([(x1 * S, y1 * S), (x2 * S, y2 * S)], fill=fill, width=width * S)


def arrow(x1, y1, x2, y2, fill=INK, width=2, head=9):
    L(x1, y1, x2, y2, fill, width)
    v = np.array([x2 - x1, y2 - y1], dtype=float)
    v /= np.linalg.norm(v)
    n = np.array([-v[1], v[0]])
    tip = np.array([x2, y2])
    p1 = tip - v * head + n * head * 0.5
    p2 = tip - v * head - n * head * 0.5
    d.polygon([tuple(tip * S), tuple(p1 * S), tuple(p2 * S)], fill=fill)


def panel(x, y, w, h, title, ref=None):
    R(x, y, w, h, fill=PANEL, outline=LINE, r=8)
    T(x + 14, y + 10, title, F(17, bold=True))
    if ref:
        T(x + w - 14, y + 13, ref, F(12.5, mono=True), fill=CODE, anchor="ra")


# --------------------------------------------------------------------------
# Example batch and the exact computations from _prepare_inputs / block_table
# --------------------------------------------------------------------------
BLOCK = 16
phase = ["decode", "chunked prefill (2nd chunk)", "decode", "prefill (new request)"]
num_prompt = np.array([10, 30, 4, 3])
num_computed = np.array([17, 12, 5, 0])
num_sched = np.array([1, 6, 1, 3])
block_ids = [[7, 2], [5, 9], [3], [11]]
num_reqs = 4

req_indices = np.repeat(np.arange(num_reqs), num_sched)                 # :1975
cu = np.cumsum(num_sched)                                               # :1739
query_pos = np.arange(cu[-1]) - np.repeat(cu - num_sched, num_sched)    # :1742-1748
positions = num_computed[req_indices] + query_pos                       # :1984
qsl = np.concatenate([[0], cu])                                         # :2060-2061
seq_lens = num_computed + num_sched                                     # :2179
slot = np.array([block_ids[r][p // BLOCK] * BLOCK + p % BLOCK          # bt.py:445-478
                 for r, p in zip(req_indices, positions)])
NT = int(cu[-1])
assert list(qsl) == [0, 1, 7, 8, 11] and list(seq_lens) == [18, 18, 6, 3]

# --------------------------------------------------------------------------
# Title
# --------------------------------------------------------------------------
T(30, 18, "vLLM V1: one mixed prefill + decode batch → FlashAttention inputs and paged KV cache",
  F(24, bold=True))
T(30, 54, "GPUModelRunner._prepare_inputs → BlockTable.compute_slot_mapping → CommonAttentionMetadata → "
  "FlashAttentionMetadataBuilder.build → FlashAttentionImpl.do_kv_cache_update / forward",
  F(13.5), fill=MUTED)

# --------------------------------------------------------------------------
# Panel 0: example batch
# --------------------------------------------------------------------------
px, py, pw, ph = 30, 84, 1760, 214
panel(px, py, pw, ph, "0 · The example batch (block_size = 16)",
      "gpu_model_runner.py:4224-4232 (execute_model)")
cols = [("row r", 70), ("req", 50), ("phase", 250), ("num_prompt_tokens", 175),
        ("num_computed_tokens", 190), ("num_scheduled_tokens", 195), ("block IDs → block_table row r", 270),
        ("new tokens' positions", 200)]
tx, ty = px + 18, py + 44
x = tx
for name, w in cols:
    T(x + 6, ty, name, F(12.5, bold=True), fill=MUTED)
    x += w
L(tx, ty + 22, tx + sum(w for _, w in cols), ty + 22, LINE)
for r in range(num_reqs):
    yy = ty + 30 + r * 30
    base, tint = COL[r]
    R(tx, yy - 4, sum(w for _, w in cols), 27, fill=tint, r=4)
    p0, p1 = positions[qsl[r]], positions[qsl[r + 1] - 1]
    vals = [str(r), NAMES[r], phase[r], str(num_prompt[r]), str(num_computed[r]), str(num_sched[r]),
            str(block_ids[r]), f"{p0}" if p0 == p1 else f"{p0} … {p1}"]
    x = tx
    for (name, w), v in zip(cols, vals):
        T(x + 6, yy, v, F(14, bold=(name == "req"), mono=name != "phase"), fill=base if name == "req" else INK)
        x += w
nx = tx + sum(w for _, w in cols) + 18
notes0 = [
    "num_scheduled_tokens_np = [1, 6, 1, 3]",
    "taken in input_batch.req_ids order (:4224-4226).",
    "Rows are not split by phase: decodes and",
    "prefills go into the same flat token axis and",
    "the same FlashAttention varlen call.",
    "B: seq_len 18 < 30 → its sample is discarded",
    "(discard_request_mask, :2089-2091).",
]
for i, s in enumerate(notes0):
    T(nx, ty + i * 21, s, F(12.5, mono=i == 0), fill=INK if i == 0 else MUTED)

# --------------------------------------------------------------------------
# Panel 1/2/3: token-aligned grid
# --------------------------------------------------------------------------
gx, gy, gw, gh = 30, 312, 1760, 524
panel(gx, gy, gw, gh, "1 · Flatten scheduled tokens   2 · per-request metadata   3 · block_table → slot_mapping",
      "GPUModelRunner._prepare_inputs  gpu_model_runner.py:1951-2188")
LBLX = gx + 18
CX = gx + 250  # first token cell x
CW = 66
RH = 44
NOTEX = CX + (NT + 1) * CW + 26

rows = [
    ("query_start_loc", "boundary"),
    ("t  (flat token idx)", "t"),
    ("req_indices", "req"),
    ("query_pos", "qpos"),
    ("positions", "pos"),
    ("input_ids", "ids"),
    ("seq_lens", "seqlen"),
    ("block_table[r]", "bt"),
    ("slot_mapping", "slot"),
]
notes = {
    "boundary": ["qsl.np[0] = 0;  qsl.np[1:n+1] = cu_num_tokens;",
                 "pad: qsl.np[n+1:] = cu_num_tokens[-1]        :2060-2066"],
    "t": ["total_num_scheduled_tokens = 1+6+1+3 = 11",
          "(num_actual_tokens in the attention metadata)"],
    "req": ["np.repeat(arange_np[:num_reqs], num_scheduled_tokens)",
            "                                              :1975"],
    "qpos": ["_get_cumsum_and_arange(num_scheduled_tokens, query_pos.np)",
             "per-request arange via cumsum offsets   :1726-1750, :1979"],
    "pos": ["num_computed_tokens[req_indices] + query_pos",
            "CPU :1984-1987;  GPU copy self.positions :2175-2178"],
    "ids": ["index_select(token_ids_cpu.flatten(),",
            "             positions + req_indices * M)   :1998-2011"],
    "seqlen": ["num_computed_tokens[:n] + num_scheduled_tokens",
               ":2179-2182;  max_seq_len = max = 18  :2315"],
    "bt": ["BlockTable.block_table rows (append_row), int32,",
           "commit_block_table → copy_to_gpu   :1971; bt.py:157-232"],
    "slot": ["block_table[r, pos // 16] * 16 + pos % 16, one Triton",
             "program per request over qsl[r]:qsl[r+1]  bt.py:432-478"],
}

grid_top = gy + 52
row_y = {}
for i, (lbl, key) in enumerate(rows):
    y = grid_top + i * RH
    row_y[key] = y
    T(LBLX, y + RH / 2, lbl, F(14, bold=True, mono=True), anchor="lm")
    for j, s in enumerate(notes[key]):
        T(NOTEX, y + 8 + j * 17, s, F(11.5, mono=True), fill=CODE if j == len(notes[key]) - 1 else MUTED)

# request span backgrounds (columns)
for r in range(num_reqs):
    x0 = CX + qsl[r] * CW
    x1 = CX + qsl[r + 1] * CW
    R(x0 + 2, grid_top + RH - 4, x1 - x0 - 4, RH * (len(rows) - 1) + 2, fill=COL[r][1], r=6)
    T((x0 + x1) / 2, grid_top + RH * len(rows) + 4, f"req {NAMES[r]} (r={r})" if qsl[r + 1] - qsl[r] > 1
      else NAMES[r], F(12.5, bold=True), fill=COL[r][0], anchor="ma")
# padding column
padx = CX + NT * CW
R(padx + 2, grid_top + RH - 4, CW - 4, RH * (len(rows) - 1) + 2, fill="#eceff3", r=6)
T(padx + CW / 2, grid_top + RH * len(rows) + 4, "pad", F(12.5, bold=True), fill=MUTED, anchor="ma")


def cell(j, key, s, color=INK, bold=False, size=14.5, mono=True):
    x = CX + j * CW
    y = row_y[key]
    R(x + 6, y + 6, CW - 12, RH - 12, fill="white", outline=LINE, r=4)
    T(x + CW / 2, y + RH / 2, s, F(size, bold=bold, mono=mono), fill=color, anchor="mm")


for t in range(NT):
    r = req_indices[t]
    base = COL[r][0]
    cell(t, "t", str(t), color=MUTED)
    cell(t, "req", str(r), color=base, bold=True)
    cell(t, "qpos", str(query_pos[t]))
    cell(t, "pos", str(positions[t]), bold=True)
    cell(t, "ids", f"{NAMES[r]}[{positions[t]}]", size=12.5)
    cell(t, "slot", str(slot[t]), color=base, bold=True)
cell(NT, "slot", "-1", color=MUTED)
cell(NT, "t", "11+", color=MUTED, size=12.5)

# per-request spans: seq_lens and block_table rows
for r in range(num_reqs):
    x0 = CX + qsl[r] * CW
    x1 = CX + qsl[r + 1] * CW
    for key, s in (("seqlen", str(seq_lens[r])),
                   ("bt", ", ".join(map(str, block_ids[r])) + (", 0…" if qsl[r + 1] - qsl[r] > 2 else ""))):
        y = row_y[key]
        R(x0 + 6, y + 6, x1 - x0 - 12, RH - 12, fill="white", outline=COL[r][0], width=1, r=4)
        T((x0 + x1) / 2, y + RH / 2, s, F(14.5, bold=True, mono=True), fill=COL[r][0], anchor="mm")
y = row_y["bt"]
R(padx + 6, y + 6, CW - 12, RH - 12, fill="white", outline=LINE, r=4)
T(padx + CW / 2, y + RH / 2, "NULL", F(11, mono=True), fill=MUTED, anchor="mm")
y = row_y["seqlen"]
R(padx + 6, y + 6, CW - 12, RH - 12, fill="white", outline=LINE, r=4)
T(padx + CW / 2, y + RH / 2, "0", F(14, mono=True), fill=MUTED, anchor="mm")

# query_start_loc ticks at request boundaries
yb = row_y["boundary"]
for r, v in enumerate(qsl):
    x = CX + v * CW
    L(x, yb + 30, x, grid_top + RH * len(rows) - 6, fill=INK, width=2)
    R(x - 17, yb + 4, 34, 24, fill=INK, r=5)
    T(x, yb + 16, str(v), F(14, bold=True, mono=True), fill="white", anchor="mm")
T(CX + (NT + 1) * CW - 4, yb + 16, "(11)", F(12.5, mono=True), fill=MUTED, anchor="rm")

# worked slot example for B crossing a block boundary
ex_y = grid_top + RH * len(rows) + 28
T(LBLX, ex_y, "Worked slot_mapping, req B (row 1, block_table[1] = [5, 9]):", F(13, bold=True))
T(LBLX + 470, ex_y,
  "pos 15 → block_table[1][15//16 = 0] = 5 → 5·16 + 15 = 95     "
  "pos 16 → block_table[1][16//16 = 1] = 9 → 9·16 + 0 = 144",
  F(12.5, mono=True), fill=COL[1][0])
T(LBLX, ex_y + 22,
  "Pad tokens (CUDA-graph padding) get slot -1 (PAD_SLOT_ID: kernel's last program, bt.py:434-443; "
  "_get_slot_mappings :4111-4113); padded block_table rows = NULL_BLOCK_ID (:2332-2334). "
  "logits_indices = qsl[1:] − 1 = [0, 6, 7, 10] (:2231).",
  F(12), fill=MUTED)

# --------------------------------------------------------------------------
# Panel 4: metadata hand-off pipeline
# --------------------------------------------------------------------------
my = 850
mh = 150
panel(30, my, 1760, mh, "4 · Hand-off to the backend", "execute_model  gpu_model_runner.py:4349-4421")
boxes = [
    ("_get_slot_mappings  :4065-4137",
     ["slot_mapping = block_table[gid]", ".slot_mapping.gpu[:num_tokens]", "pad tail with -1"]),
    ("_build_attention_metadata  :2277",
     ["CommonAttentionMetadata(  :2426-2443", "query_start_loc, seq_lens, block_table_tensor,",
      "slot_mapping, num_actual_tokens=11,", "max_query_len=6, max_seq_len=18, causal=True)"]),
    ("FlashAttentionMetadataBuilder.build  fa:815",
     ["copies the same tensors into", "FlashAttentionMetadata  fa:511-526, 996-1003",
      "+ scheduler_metadata (get_scheduler_metadata)", "use_cascade = common_prefix_len > 0 → False"]),
    ("set_forward_context  :4409",
     ["attn_metadata per layer +", "slot_mapping per layer; each attention", "layer then writes (5) and reads (6)"]),
]
bx = 48
bws = [330, 470, 470, 380]
for (title, lines), bw in zip(boxes, bws):
    R(bx, my + 40, bw, 98, fill="white", outline=LINE, r=6)
    T(bx + 10, my + 47, title, F(12.5, bold=True, mono=True), fill=CODE)
    for i, s in enumerate(lines):
        T(bx + 10, my + 68 + i * 17, s, F(11.8, mono=True), fill=INK)
    if bx + bw + 30 < 1790:
        arrow(bx + bw + 3, my + 89, bx + bw + 25, my + 89, fill=MUTED, width=2, head=8)
    bx += bw + 28

# --------------------------------------------------------------------------
# Panel 5: write into paged KV cache
# --------------------------------------------------------------------------
ky = 1014
kh = 572
kx, kw = 30, 900
panel(kx, ky, kw, kh, "5 · Write: new K/V scattered by slot_mapping", "FlashAttentionImpl.do_kv_cache_update  fa:1511-1545")
T(kx + 16, ky + 40, "reshape_and_cache_flash(key, value, key_cache, value_cache, slot_mapping, …)",
  F(12.5, bold=True, mono=True), fill=CODE)
T(kx + 16, ky + 60, "kv_cache [num_blocks, H_kv, 16, 2·D] → .transpose(1,2).split(D) → key_cache,"
  " value_cache [num_blocks, 16, H_kv, D]  (fa:1527)", F(11.5, mono=True), fill=MUTED)
T(kx + 16, ky + 77, "token t → block slot_mapping[t] // 16, offset slot_mapping[t] % 16"
  "  (slot = block·16 + offset, bt.py:475-476)", F(11.5, mono=True), fill=MUTED)

SW = 26
blk_x = kx + 150
order = [(7, 0, 0), (2, 0, 1), (5, 1, 0), (9, 1, 1), (3, 2, 0), (11, 3, 0)]  # (block, req, logical blk idx)
by0 = ky + 112
T(blk_x, by0 - 14, "offset →  0 … 15", F(11, mono=True), fill=MUTED)
for i, (b, r, li) in enumerate(order):
    y = by0 + i * 48
    base, tint = COL[r]
    T(kx + 16, y + 6, f"block {b}", F(14, bold=True, mono=True), fill=base)
    T(kx + 16, y + 24, f"{NAMES[r]}: block_table[{r}][{li}]", F(10.5, mono=True), fill=MUTED)
    new_t = []
    for o in range(BLOCK):
        p = li * BLOCK + o
        x = blk_x + o * SW
        if p < num_computed[r]:
            R(x, y, SW - 3, 30, fill=tint, outline=tint, r=3)
            T(x + (SW - 3) / 2, y + 15, str(p), F(9.5, mono=True), fill=base, anchor="mm")
        elif p < seq_lens[r]:
            t = int(qsl[r] + (p - num_computed[r]))
            new_t.append((t, b * BLOCK + o))
            R(x, y, SW - 3, 30, fill=base, outline=INK, width=1, r=3)
            T(x + (SW - 3) / 2, y + 15, str(p), F(10, bold=True, mono=True), fill="white", anchor="mm")
        else:
            R(x, y, SW - 3, 30, fill="white", outline=LINE, r=3)
    ts = [t for t, _ in new_t]
    ss = [s for _, s in new_t]
    if not ts:
        T(blk_x + BLOCK * SW + 12, y + 15, "(full, no writes)", F(12, mono=True), fill=MUTED, anchor="lm")
        continue
    lbl = (f"t{ts[0]} → slot {ss[0]}" if len(ts) == 1
           else f"t{ts[0]}–t{ts[-1]} → slots {ss[0]}–{ss[-1]}")
    T(blk_x + BLOCK * SW + 12, y + 15, "← " + lbl, F(12, bold=True, mono=True), fill=base, anchor="lm")

ly = by0 + 6 * 48 + 8
R(kx + 16, ly, 22, 16, fill="#dfe3e8", r=3)
T(kx + 44, ly + 8, "cached by earlier steps (number = logical position)", F(11.5), fill=MUTED, anchor="lm")
R(kx + 16, ly + 22, 22, 16, fill="#555", outline=INK, r=3)
T(kx + 44, ly + 30, "written in this step from key/value[t]", F(11.5), fill=MUTED, anchor="lm")
R(kx + 16, ly + 44, 22, 16, fill="white", outline=LINE, r=3)
T(kx + 44, ly + 52, "allocated, still empty", F(11.5), fill=MUTED, anchor="lm")
T(kx + 470, ly + 8, "Physical blocks need not be contiguous or ordered:", F(11.5), fill=MUTED, anchor="lm")
T(kx + 470, ly + 30, "A's logical blocks [0,1] live in physical [7, 2].", F(11.5), fill=MUTED, anchor="lm")
T(kx + 470, ly + 52, "slot_mapping covers only scheduled tokens (11).", F(11.5), fill=MUTED, anchor="lm")

# --------------------------------------------------------------------------
# Panel 6: read with flash_attn_varlen_func
# --------------------------------------------------------------------------
rx, rw = 944, 846
panel(rx, ky, rw, kh, "6 · Read: one varlen call for all 4 requests", "FlashAttentionImpl.forward  fa:1330-1479")
args = [
    ("q", "query[:num_actual_tokens]", "11 rows, flat order of (1)"),
    ("k, v", "key_cache, value_cache", "paged cache from (5), not key/value"),
    ("cu_seqlens_q", "query_start_loc", "[0, 1, 7, 8, 11]"),
    ("seqused_k", "seq_lens", "[18, 18, 6, 3]"),
    ("max_seqlen_q", "max_query_len", "6   (max num_scheduled_tokens, :4227)"),
    ("max_seqlen_k", "max_seq_len", "18"),
    ("block_table", "block_table", "[[7,2],[5,9],[3],[11]]"),
    ("causal", "causal", "True"),
]
T(rx + 16, ky + 40, "_FA4_DENSE_ATTENTION_KERNEL(...) → flash_attn_varlen_func  (fa:114-116, 1454-1479)",
  F(12.5, bold=True, mono=True), fill=CODE)
for i, (a, b, c) in enumerate(args):
    yy = ky + 64 + i * 19
    T(rx + 22, yy, f"{a:<13}= {b}", F(12, mono=True), fill=INK)
    T(rx + 400, yy, c, F(12, mono=True), fill=MUTED)

# causal mask for req B
my0 = ky + 250
T(rx + 16, my0, "Request B inside that call: queries q[1:7] × keys 0..17 gathered via block_table[1]",
  F(13, bold=True), fill=COL[1][0])
MC = 19
mx0 = rx + 150
mtop = my0 + 44
L(mx0 + 16 * MC - 1, mtop - 22, mx0 + 16 * MC - 1, mtop + 6 * MC + 4, fill=INK, width=2)
T(mx0 + 8 * MC, mtop - 20, "physical block 5  (keys 0–15)", F(11, bold=True, mono=True), fill=COL[1][0], anchor="ma")
T(mx0 + 17 * MC, mtop - 20, "9", F(11, bold=True, mono=True), fill=COL[1][0], anchor="la")
for k in range(18):
    T(mx0 + k * MC + MC / 2, mtop + 6 * MC + 6, str(k), F(9, mono=True), fill=MUTED, anchor="ma")
for i in range(6):
    t = 1 + i
    p = positions[t]
    T(mx0 - 8, mtop + i * MC + MC / 2, f"t{t} (pos {p})", F(11, mono=True), fill=INK, anchor="rm")
    for k in range(18):
        x = mx0 + k * MC
        y = mtop + i * MC
        if k <= p:
            fill = COL[1][0] if k >= num_computed[1] else COL[1][1]
            R(x + 1, y + 1, MC - 2, MC - 2, fill=fill, r=2)
        else:
            R(x + 1, y + 1, MC - 2, MC - 2, fill="white", outline="#e3e7ec", r=2)
T(mx0 + 9 * MC, mtop + 6 * MC + 22, "key position k", F(11), fill=MUTED, anchor="ma")
nx6 = mx0 + 18 * MC + 70 + 20
mnotes = [
    ("query i of request r sits at position", INK),
    ("seq_lens[r] − query_len[r] + i", INK),
    ("(context_len | query_len, fa:512-518)", CODE),
    ("so causal=True lets pos p see keys ≤ p:", INK),
    ("light = cached keys 0..11,", MUTED),
    ("dark = keys 12..17 just written in (5).", MUTED),
]
for i, (s, c) in enumerate(mnotes):
    T(nx6 - 40, mtop - 20 + i * 19, s, F(11.5, mono=i in (1, 2)), fill=c)
fy = mtop + 6 * MC + 46
T(rx + 16, fy, "Decodes A and C are just 1-row queries in the same call: A's t0 (pos 17) reads 18 keys via"
  " blocks [7, 2];", F(12), fill=INK)
T(rx + 16, fy + 19, "C's t7 reads 6 keys via [3]; D's t8–t10 is a fresh 3×3 causal prefill in block 11.",
  F(12), fill=INK)
T(rx + 16, fy + 41, "The non-cascade forward passes k=key_cache, v=value_cache (fa:1456-1457), so the new K/V",
  F(11.5), fill=MUTED)
T(rx + 16, fy + 59, "must already be in the cache: forward_includes_kv_cache_update = False (fa:365) → the write"
  " (5) is a", F(11.5), fill=MUTED)
T(rx + 16, fy + 77, "separate do_kv_cache_update call made before this read.", F(11.5), fill=MUTED)

# footer
T(30, H - 34, "Source: vllm-project/vllm @ 4c2d2776 — vllm/v1/worker/gpu_model_runner.py (:N), vllm/v1/worker/"
  "block_table.py (bt.py), vllm/v1/attention/backends/flash_attn.py (fa:N).  Assumes one KV-cache group, "
  "no spec decode, DCP/PCP = 1, no cascade.", F(11.5), fill=MUTED)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mixed-batch-attn.png")
img.save(out, optimize=True)
print(out, img.size)
