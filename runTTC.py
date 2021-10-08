#  runTTC.py
# This program reads the actual preference data that may contain students' privacy
# and apply TTC.  The output is written to afterTTC and is a directed graph
# which represents the result of conversions.
# 出力されるデータのファイル名を'afterTTC.csv'としています
# afterTTC.csv の各行には, 左から順に
#「交換希望者番号」「交換前のスロット」「->」「交換後のスロット」「交換相手」が出力されます

import csv
import TTC

try:
    with open('preference.csv') as f:
        reader = csv.reader(f)
        orig_preferences = [row for row in reader]
except Exception:
    with open('test.csv') as f:
        reader = csv.reader(f)
        orig_preferences = [row for row in reader]


# apply TTC
all_cycles, all_cycles2, residual = TTC.TTC(orig_preferences)


# 全てのサイクルの辺 and all isolated points のリストを作成する
cycles_or_points = []

for cycle in all_cycles:
    cycles_or_points += cycle

for cycle in all_cycles2:
    cycles_or_points += cycle

# サイクルの辺に含まれない node i に対して, [i, -1] を追加しておく
for j in residual.nodes:
    cycles_or_points.append([j, -1])

# perform the lexicographic sort on edges (= two-elements lists)
cycles_or_points.sort()
#print(cycles_or_points)


# define finite mappings from slot IDs (from 1 to 56) to dates

# closed interval
# NB: range(x, y) is [x, x+1, ..., y-1] and does NOT include y
def CI(m,n):
    return list(range(m,n+1))

def expand_to_dict(ll):
    dict = {}
    for value, ran in ll:
        for i in ran:
            dict[i] = value
    return dict

# 日付: 1~18:9/21, 19~37:9/22, 38~56:9/24
days = [
    ('9/21 ', CI(1,18)),
    ('9/22 ', CI(19,37)),
    ('9/24 ', CI(38,56)),
]
day_of_slot = expand_to_dict(days)

# 時: (1~6 or 19~24 or 38~43):14,
# (7~12 or 25~30 or 44~49):15,
# (13~18 or 31~36 or 50~55):16,
# (37 or 56):17    
times = [
    ('14', CI(1,6) + CI(19,24) + CI(38,43)),
    ('15', CI(7,12) + CI(25,30) + CI(44,49)),
    ('16', CI(13,18) + CI(31,36) + CI(50,55)),
    ('17', [37,56]),
]
time_of_slot = expand_to_dict(times)

# 分:slot が (((6で割った余り) + 5) を 6 で割った余り)×10
# slot が 1~37 :  min/10 = (slot + 5) を 6 で割った余り
# slot が 38~56 : min/10 = (slot + 4) を 6 で割った余り
minute_of_slot = {}
for slot in CI(1,37):
    minute_of_slot[slot] = ((slot+5)%6) * 10
for slot in CI(38,56):
    minute_of_slot[slot] = ((slot+4)%6) * 10

# afterTTC.csvファイルの作成

g = open('afterTTC.csv', 'w')

for i, applicant in enumerate(orig_preferences):
    try:
        g.write(applicant[57] + ',' + applicant[58] + ',' + applicant[59] + ',' + applicant[60] + ',' + applicant[61] + ',')
    except Exception:
        g.write('')
    # applicant No.i の, 交換前のスロットを書き込む
    slot = int(applicant[0])
    # write 日付, time, min
    g.write(day_of_slot[slot])
    g.write(time_of_slot[slot])
    g.write('{:2}'.format(minute_of_slot[slot]))
    # write delimiters
    g.write(',' + '->' + ',')

    # applicant No.i の交換が成立した場合, 交換後のスロットを書き込む
    ID_or_failure = cycles_or_points[i][1]
    if ID_or_failure != -1:
        newslot = int(orig_preferences[ID_or_failure-1][0])
        g.write(day_of_slot[newslot])
        g.write(time_of_slot[newslot])
        g.write('{:2}'.format(minute_of_slot[newslot]))
        g.write(',' + str(ID_or_failure) + '\n')
    else:
        g.write('no match' + '\n')

g.close()

#list(map(print, all_cycles))
#print(residual.nodes)
#list(map(print, all_cycles2))
print(residual.nodes)

