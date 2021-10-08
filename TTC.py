#  TTC.py
# preferenceデータから有向グラフを作り, TTC を適用するプログラム

import networkx as nx

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

# input l : list read from some CSV
# output all_cycles, all_cycles2, residual
def TTC(l):
    # preference data に載っている人数
    number_of_applicants = len(l)
    # preference データから有向グラフを作る
    preferenceGraph = nx.DiGraph()
    # 頂点の追加(個数 = number_of_applicants)
    i = 1
    while i <= number_of_applicants:
        preferenceGraph.add_node(i)
        i = i + 1
    # 有向辺の追加
    # 「A の◯スロット = B の交換前のスロット」が成り立つとき, 有向辺 A -> B を追加
    i = 1
    while i <= number_of_applicants:
        j = 1
        while j <= number_of_applicants:
            if (i != j) and (l[i-1][int(l[j-1][0])] == '1'):
                preferenceGraph.add_edge(i,j)
            j = j + 1
        i = i + 1
    # ◯辺のサイクルの計算
    all_cycles, residual = Pull_out_all_cycles(preferenceGraph)
    preferenceGraph2 = residual

    # 有向辺の追加2
    # 「A の△スロット = B の交換前のスロット」が成り立つとき, 有向辺 A -> B を追加
    already_removed_nodes = set()
    for x in sum(sum(all_cycles, []), []):
        already_removed_nodes.add(x)
    i = 1
    while i <= number_of_applicants:
        j = 1
        while j <= number_of_applicants:
            if (i != j) and (l[i-1][int(l[j-1][0])] == '2')  and not({i, j} & already_removed_nodes):
                preferenceGraph2.add_edge(i,j)
            j = j + 1
        i = i + 1
    # △辺のサイクルの計算
    all_cycles2, residual = Pull_out_all_cycles(preferenceGraph2)
    return all_cycles, all_cycles2, residual
