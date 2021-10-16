#  TTC.py
# preferenceデータから有向グラフを作り, TTC を適用するプログラム

import networkx as nx

import preference as P


# Parameters
# l : list, supposedly read from preference.csv

##########################################    

# input preferenceGraph:DiGraph
# output (cycle:list, residual:DiGraph)
# サイクルが見つからない場合、cycle = [] とする
def Pull_out_cycle(preferenceGraph):
#    cycles = nx.simple_cycles(preferenceGraph)
#    cyclelist = list(cycles)
#    if len(cyclelist) != 0:
#        cycle = cyclelist[0]
#    else:
#        cycle = []
    try:
        cycle = nx.find_cycle(preferenceGraph)
    except nx.NetworkXNoCycle:
        cycle = []
    residual = nx.DiGraph.copy(preferenceGraph)
#    for i in cycle:
#        residual.remove_node(i)
    cycle = [list(x) for x in cycle]
    nodes = sum(cycle, [])
    residual.remove_nodes_from(nodes)
    return cycle, residual
    #print(cyclelist)

# input preferenceGraph
# output all_cycles:list of lists, residual
def Pull_out_all_cycles(preferenceGraph):
    all_cycles = []
    cycle, residual = Pull_out_cycle(preferenceGraph)
    while len(cycle) != 0:
        all_cycles.append(cycle)
        cycle, residual = Pull_out_cycle(residual)
    return all_cycles, residual

# input pref : matrix read from the preference CSV
# output all_cycles, all_cycles2, residual
def TTC(pref):
    # preference データから有向グラフを作る
    preferenceGraph = nx.DiGraph()
    # 頂点の追加
    for row in pref:
        preferenceGraph.add_node(row.node_ID())
    # 有向辺の追加
    # 「A の◯スロット = B の交換前のスロット」が成り立つとき, 有向辺 A -> B を追加
    for A in pref:
        A_maru = A.maru_slots()
        A_ID = A.node_ID()
        for B in pref:
            B_slot = B.slot()
            B_ID = B.node_ID()
            if A_ID != B_ID and B_slot in A_maru:
                preferenceGraph.add_edge(A_ID, B_ID)
    # ◯辺のサイクルの計算
    all_cycles, residual = Pull_out_all_cycles(preferenceGraph)

    # 有向辺の追加2
    preferenceGraph2 = residual
    # 「A の△スロット = B の交換前のスロット」が成り立つとき, 有向辺 A -> B を追加
    already_matched_nodes = set(sum(sum(all_cycles, []), []))
    for A in pref:
        if A_ID in already_matched_nodes:
            continue
        A_sankaku = A.sankaku_slots()
        A_ID = A.node_ID()
        for B in pref:
            B_slot = B.slot()
            B_ID = B.node_ID()
            if not B_ID in already_matched_nodes and A_ID != B_ID and B_slot in A_sankaku:
                preferenceGraph2.add_edge(A_ID, B_ID)
    # △辺のサイクルの計算
    all_cycles2, residual = Pull_out_all_cycles(preferenceGraph2)
    return all_cycles, all_cycles2, residual
