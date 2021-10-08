#  TTC.py
# preferenceデータから有向グラフを作り, TTC を適用するプログラム
# 出力されるデータのファイル名を'afterTTC.csv'としています
# afterTTC.csv の各行には, 左から順に
#「交換希望者番号」「交換前のスロット」「->」「交換後のスロット」「交換相手」が出力されます

import csv
import random
import pprint
import networkx as nx
#import matplotlib.pyplot as plot

number_of_applicant = 30 # preference.csv に載っている人数


with open('preference.csv') as f:
    reader = csv.reader(f)
    l = [row for row in reader]


        

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

# input number_of_applicant, l
# output all_cycles, all_cycles2, residual
def TTC(number_of_applicant, l):
    # preference データから有向グラフを作る
    preferenceGraph = nx.DiGraph()
    # 頂点の追加(個数 = number_of_applicant)   
    i = 1
    while i <= number_of_applicant:
        preferenceGraph.add_node(i)
        i = i + 1
    # 有向辺の追加
    # 「A の◯スロット = B の交換前のスロット」が成り立つとき, 有向辺 A -> B を追加
    i = 1
    while i <= number_of_applicant:
        j = 1
        while j <= number_of_applicant:
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
    while i <= number_of_applicant:
        j = 1
        while j <= number_of_applicant:
            if (i != j) and (l[i-1][int(l[j-1][0])] == '2')  and not({i, j} & already_removed_nodes):
                preferenceGraph2.add_edge(i,j)
            j = j + 1
        i = i + 1
    # △辺のサイクルの計算
    all_cycles2, residual = Pull_out_all_cycles(preferenceGraph2)
    return all_cycles, all_cycles2, residual



all_cycles, all_cycles2, residual = TTC(number_of_applicant, l)

# afterTTC.cvsファイルの作成

# 全てのサイクルの辺のリストを作成する
allCycle = []
i = 1
while i <= len(all_cycles):
    j = 1
    while j <= len(all_cycles[i-1]):
        allCycle.append(all_cycles[i-1][j-1])
        j = j + 1
    i = i + 1

i = 1
while i <= len(all_cycles2):
    j = 1
    while j <= len(all_cycles2[i-1]):
        allCycle.append(all_cycles2[i-1][j-1])
        j = j + 1
    i = i + 1

# サイクルの辺に含まれない node i に対して, [i, -1] を追加しておく
for j in residual.nodes:
    allCycle.append([j, -1])

allCycle.sort()
#print(allCycle)

# afterTTC.csvファイルの作成

g = open('afterTTC.csv', 'w')

i = 1
while i <= number_of_applicant:
    g.write(l[i-1][57] + ',' + l[i-1][58] + ',' + l[i-1][59] + ',' + l[i-1][60] + ',' + l[i-1][61] + ',')
    # applicant No.i の, 交換前のスロットを書き込む
    # 日付:int(l[i-1][0]) が 1~18:9/21, 19~37:9/22, 38~56:9/24
    if 1 <= int(l[i-1][0]) <= 18 :
        g.write('9/21 ')
    elif 19 <= int(l[i-1][0]) <= 37:
        g.write('9/22 ')
    else:
        g.write('9/24 ')
    # 時:int(l[i-1][0]) が (1~6 or 19~24 or 38~43):14, (7~12 or 25~30 or 44~49):15, (13~18 or 31~36 or 50~55):16, (37 or 56):17
    if (1 <= int(l[i-1][0]) <= 6) or (19 <= int(l[i-1][0]) <= 24) or (38 <= int(l[i-1][0]) <= 43):
        g.write('14:')
    elif (7 <= int(l[i-1][0]) <= 12) or (25 <= int(l[i-1][0]) <= 30) or (44 <= int(l[i-1][0]) <= 49):
        g.write('15:')
    elif (13 <= int(l[i-1][0]) <= 18) or (31 <= int(l[i-1][0]) <= 36) or (50 <= int(l[i-1][0]) <= 55):
        g.write('16:')
    else:
        g.write('17:')
    # 分:int(l[i-1][0]) が (((6で割った余り) + 5) を 6 で割った余り)×10
    # int(l[i-1][0]) が 1~37 : (((6で割った余り) + 5) を 6 で割った余り)
    # int(l[i-1][0]) が 38~56 : ((6で割った余り) + 4) を 6 で割った余り
    if (1 <= int(l[i-1][0]) <= 37):
        g.write(str(( (int(l[i-1][0])%6) +5)%6) + str(0) + ',' + '->' + ',')
    else:
        g.write(str(( (int(l[i-1][0])%6) +4)%6) + str(0) + ',' + '->' + ',')
    
    # applicant No.i の交換が成立した場合, 交換後のスロットを書き込む
    if allCycle[i-1][1] != -1:
        # 日付:int(l[(allCycle[i-1][1])-1][0]) が 1~18:9/21, 19~37:9/22, 38~56:9/24
        if 1 <= int(l[(allCycle[i-1][1])-1][0]) <= 18 :
            g.write('9/21 ')
        elif 19 <= int(l[(allCycle[i-1][1])-1][0]) <= 37:
            g.write('9/22 ')
        else:
            g.write('9/24 ')
        # 時:int(l[(allCycle[i-1][1])-1][0]) が (1~6 or 19~24 or 38~43):14, (7~12 or 25~30 or 44~49):15, (13~18 or 31~36 or 50~55):16, (37 or 56):17
        if (1 <= int(l[(allCycle[i-1][1])-1][0]) <= 6) or (19 <= int(l[(allCycle[i-1][1])-1][0]) <= 24) or (38 <= int(l[(allCycle[i-1][1])-1][0]) <= 43):
            g.write('14:')
        elif (7 <= int(l[(allCycle[i-1][1])-1][0]) <= 12) or (25 <= int(l[(allCycle[i-1][1])-1][0]) <= 30) or (44 <= int(l[(allCycle[i-1][1])-1][0]) <= 49):
            g.write('15:')
        elif (13 <= int(l[(allCycle[i-1][1])-1][0]) <= 18) or (31 <= int(l[(allCycle[i-1][1])-1][0]) <= 36) or (50 <= int(l[(allCycle[i-1][1])-1][0]) <= 55):
            g.write('16:')
        else:
            g.write('17:')
        # 分:int(l[(allCycle[i-1][1])-1][0]) が (((6で割った余り) + 5) を 6 で割った余り)
        if (1 <= int(l[(allCycle[i-1][1])-1][0]) <= 37):
            g.write(str((( (int(l[(allCycle[i-1][1])-1][0])%6) +5)%6)) + str(0))
        else:
            g.write(str((( (int(l[(allCycle[i-1][1])-1][0])%6) +4)%6)) + str(0))
        g.write(',' + str(allCycle[i-1][1]) + '\n')
    else:
        g.write('no match' + '\n')
    i = i + 1



#list(map(print, all_cycles))
#print(residual.nodes)
#list(map(print, all_cycles2))
print(residual.nodes)

     

g.write('end')
f.close()
g.close()
