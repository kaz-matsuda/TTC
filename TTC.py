#  TTC.py
# preferenceデータから有向グラフを作り, TTC を適用するプログラム

import csv
import random
import pprint
import networkx as nx
#import matplotlib.pyplot as plot

student = 10 # S券交換を希望している学生の人数


with open('test.csv') as f:
    reader = csv.reader(f)
    l = [row for row in reader]
#print(l)

        
g = open('afterTTC.txt', 'w')
##########################################



i = 1
j = 1 
k = 0
m = 0
n = 1
line = ''
sublist = ''
connectnode = ''
status = ''


# preference データから有向グラフを作る

preferenceGraph = nx.DiGraph()

# 頂点の追加(個数 = student)
while i <= student:
    preferenceGraph.add_node(i)
    i = i + 1

# 有向辺の追加
# 「A の◯スロット = B の交換前のスロット」が成り立つとき, 有向辺 A -> B を追加
while i <= student:
    while j <= student:
        if (i != j) and (l[i-1][int(l[j-1][0])] == '1'):
            preferenceGraph.add_edge(i,j)
        j = j + 1
    i = i + 1
    j = 1


    
# input preferenceGraph:DiGraph
# output (cycle:list, residual:DiGraph)
def TTC(preferenceGraph)
    






# 有向辺の追加
# 「A の◯スロット = B の交換前のスロット」が成り立つとき, 有向辺 A -> B を追加
i = 1
while i <= student:
    while j <= student:
        if (i != j) and (l[i-1][int(l[j-1][0])] == '1'):
            preferenceGraph.add_edge(i,j)
        j = j + 1

    i = i + 1
    j = 1

#print(preferenceGraph.edges)    
 
cycles = nx.simple_cycles(preferenceGraph)
cyclelist = list(cycles)

print(cyclelist)

#print(len(cyclelist))

#while k <= len(cyclelist):
#    exchangeStudentList. 
    


#while string[i] != 'end':
#    line = string[i].rstrip('\n')

#while i <= student:
#    print(string[i])
#    i = i + 1



g.write('end')
f.close()
g.close()
