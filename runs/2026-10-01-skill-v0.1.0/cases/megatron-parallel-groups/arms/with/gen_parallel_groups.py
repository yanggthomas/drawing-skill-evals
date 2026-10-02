"""Generate parallel-groups.dot for Megatron-Core (parallel_state.py @ e998be07).

Group lists below are the exact output of the source's own RankGenerator for
tp=2, pp=4, cp=1, ep=1, world=16, order="tp-cp-ep-dp-pp".
"""

TP, DP, PP, GPN = 2, 2, 4, 8
tp = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11], [12, 13], [14, 15]]
dp = [[0, 2], [1, 3], [4, 6], [5, 7], [8, 10], [9, 11], [12, 14], [13, 15]]
pp = [[0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15]]
mp = [[0, 1, 4, 5, 8, 9, 12, 13], [2, 3, 6, 7, 10, 11, 14, 15]]
emb = [[0, 12], [1, 13], [2, 14], [3, 15]]

MP_COLORS = [("#E8F4FD", "#2E86AB"), ("#E1BEE7", "#6A1B9A")]  # secondary, workflow
EMB_RED, PP_CROSS, DP_GOLD, TP_GREEN = "#B71C1C", "#E76F51", "#B8860B", "#2E7D32"


def gid(groups, r):
    for i, g in enumerate(groups):
        if r in g:
            return i, g
    return None, None


def fmt(g):
    return "{" + ",".join(map(str, g)) + "}"


L = []
a = L.append
a('''digraph megatron_groups {
graph [rankdir=TB, bgcolor="white", fontname="Helvetica", pad="0.4", nodesep=0.35, ranksep=0.55,
       splines=spline, newrank=true, labelloc=t, fontsize=20,
       label=<<b>Megatron-Core process groups: 16 GPUs (2 nodes x 8), TP=2, PP=4, CP=EP=1, so DP = 16 / (2*4*1) = 2</b><br/><font point-size="12">megatron/core/parallel_state.py @ e998be07, initialize_model_parallel(), default order "tp-cp-ep-dp-pp" (L638); model_size / data_parallel_size L849-859</font><br/> >];
edge [color="#555555", fontname="Helvetica", fontsize=10];
node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10, margin="0.08,0.04"];''')

for n in range(2):
    a(f'subgraph cluster_node{n} {{ label=<<b>Node {n}</b>: global ranks {n*8}-{n*8+7} (node = rank // 8)>; '
      f'fontsize=15; labelloc=b; style="dashed,rounded"; color="#888888"; bgcolor="#F5F5F5"; margin=14;')
    for s in range(PP):
        if s * TP * DP // GPN != n:
            continue
        a(f'subgraph cluster_stage{s} {{ label=<<b>pp_rank {s}</b> (pipeline stage {s})>; fontsize=12; labelloc=b; '
          f'style="rounded"; color="#BBBBBB"; bgcolor="white";')
        for d in range(DP):
            ti = s * DP + d
            a(f'subgraph cluster_tp{ti} {{ label=<<b>TP group {ti}</b> {fmt(tp[ti])}>; fontsize=10; '
              f'fontcolor="{TP_GREEN}"; style="rounded,bold"; color="{TP_GREEN}"; bgcolor="#F1F8E9";')
            for t in range(TP):
                r = t + d * TP + s * TP * DP
                di, dg = gid(dp, r)
                pi, pg = gid(pp, r)
                mi, _ = gid(mp, r)
                ei, eg = gid(emb, r)
                fill, bord = MP_COLORS[mi]
                if eg:
                    e = f'<font color="{EMB_RED}"><b>EMB {ei} {fmt(eg)}</b></font>'
                else:
                    e = '<font color="#999999">EMB: none</font>'
                lab = (
                    '<<table border="0" cellspacing="0" cellpadding="1">'
                    f'<tr><td align="left"><b><font point-size="13">rank {r}</font></b>   node {r // GPN}, local GPU {r % GPN}</td></tr>'
                    f'<tr><td align="left"><font point-size="9" color="#444444">tp={t} dp={d} pp={s}: {t}+2*{d}+4*{s} = {r}</font></td></tr>'
                    f'<tr><td align="left"><font color="{TP_GREEN}">TP {ti} {fmt(tp[ti])}</font>  <font color="{DP_GOLD}">DP {di} {fmt(dg)}</font></td></tr>'
                    f'<tr><td align="left">PP {pi} {fmt(pg)}  <font color="{bord}"><b>MP {mi}</b></font></td></tr>'
                    f'<tr><td align="left">{e}</td></tr></table>>'
                )
                extra = f', penwidth=3, color="{EMB_RED}"' if eg else f', color="{bord}"'
                a(f'r{r} [label={lab}, fillcolor="{fill}"{extra}];')
            a('}')
        a('}')
    a('}')

# Pipeline groups: p2p chain along pp_rank (tp, dp coordinates fixed).
for i, g in enumerate(pp):
    for x, y in zip(g, g[1:]):
        if x // GPN != y // GPN:
            lab = f', label=<<font color="{PP_CROSS}"><b>PP {i}: node 0 to node 1</b></font>>' if i == 0 else ""
            a(f'r{x} -> r{y} [penwidth=2.4, tailport=s, headport=n, color="{PP_CROSS}"{lab}];')
        else:
            a(f'r{x} -> r{y} [penwidth=1.4, tailport=s, headport=n];')

# Data-parallel groups: same tp/pp coordinates, dp varies (stride 2).
for g in dp:
    a(f'r{g[0]} -> r{g[1]} [dir=none, style=dashed, color="{DP_GOLD}", penwidth=1.8, tailport=n, headport=n];')

legend = f'''<<table border="1" cellborder="1" cellspacing="0" cellpadding="5" color="#888888" bgcolor="white">
<tr><td colspan="4" bgcolor="#F4D35E"><b>Assignment rule: RankGenerator (L487-570) + generate_masked_orthogonal_rank_groups (L268-374)</b></td></tr>
<tr><td colspan="4" align="left">1. order "tp-cp-ep-dp-pp" becomes "tp-cp-gtp_remat-ep-dp-pp" (_inject_gtp_remat_axis L602-618, called at L891). cp, gtp_remat and ep are size 1, so ordered sizes = [tp 2, dp 2, pp 4].<br align="left"/>
2. The leftmost axis gets the smallest stride:   <b>global_rank = tp_rank + 2*dp_rank + 4*pp_rank</b>   (docstring eq. (1), L291).<br align="left"/>
3. get_ranks(token): ranks that differ <i>only</i> on the masked axes form one group. The unmasked coordinates give the group index.<br align="left"/>
4. node = rank // 8. This assumes the launcher puts adjacent ranks on the same box (docstring L800-803). As a result, TP and DP stay inside a node, and PP and MP span nodes.<br align="left"/></td></tr>
<tr><td bgcolor="#EEEEEE"><b>Group (encoding)</b></td><td bgcolor="#EEEEEE"><b>Built by</b></td><td bgcolor="#EEEEEE"><b>Axis varied</b></td><td bgcolor="#EEEEEE"><b>Groups for this config</b></td></tr>
<tr><td align="left"><font color="{TP_GREEN}"><b>Tensor-parallel</b> (green box)</font></td><td align="left">get_ranks('tp')  L1226</td><td>tp, stride 1</td><td align="left">8 groups of 2: {{0,1}} {{2,3}} {{4,5}} ... {{14,15}}</td></tr>
<tr><td align="left"><font color="{DP_GOLD}"><b>Data-parallel</b> (dashed gold)</font></td><td align="left">get_ranks('dp')  L1115<br/>('dp-cp' L997 is identical, cp=1)</td><td>dp, stride 2</td><td align="left">8 groups of 2: {{0,2}} {{1,3}} {{4,6}} {{5,7}} {{8,10}} {{9,11}} {{12,14}} {{13,15}}</td></tr>
<tr><td align="left"><b>Pipeline-parallel</b> (arrows)</td><td align="left">get_ranks('pp')  L1302</td><td>pp, stride 4</td><td align="left">4 groups of 4: {{0,4,8,12}} {{1,5,9,13}} {{2,6,10,14}} {{3,7,11,15}}<br/><font color="{PP_CROSS}">the stage 1 to stage 2 hop crosses node 0 to node 1</font></td></tr>
<tr><td align="left"><b>Model-parallel</b> (fill colour)</td><td align="left">get_ranks('tp-gtp_remat-pp')  L1209</td><td>tp and pp</td><td align="left"><font color="#2E86AB"><b>MP 0 (blue)</b></font> {{0,1,4,5,8,9,12,13}}, all dp_rank 0<br/><font color="#6A1B9A"><b>MP 1 (purple)</b></font> {{2,3,6,7,10,11,14,15}}, all dp_rank 1</td></tr>
<tr><td align="left"><font color="{EMB_RED}"><b>Embedding</b> (red border)</font></td><td align="left">default_embedding_ranks(pp group)<br/>L580-586, applied at L1331</td><td>first and last<br/>rank of each PP group</td><td align="left">4 groups of 2: {{0,12}} {{1,13}} {{2,14}} {{3,15}}. Ranks 4-11 are in no embedding group.<br/><font color="#666666">(position-embedding = first stage only: {{0}} {{1}} {{2}} {{3}}, L589-592, L1342)</font></td></tr>
</table>>'''
for st in range(PP):
    row = [f'r{st*4+k}' for k in range(4)]
    a('{rank=same; ' + '; '.join(row) + ';}')
    a(' -> '.join(row) + ' [style=invis, weight=10];')
a(f'legend [shape=plaintext, style="", label={legend}];')
a('}')

open("parallel-groups.dot", "w").write("\n".join(L) + "\n")
