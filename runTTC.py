#  runTTC.py
# This program reads the actual preference data that may contain students' privacy,
# and applies TTC to them.
# The output is written to afterTTC.csv, which is a collection of the edges of
# a directed graph representing the exchanges of the slots.
# 出力されるデータのファイル名を'afterTTC.csv'としています
# afterTTC.csv の各行には, 左から順に
#「交換希望者番号」「交換前のスロット」「->」「交換後のスロット」「交換相手」が出力されます

import sys
import random
import csv
import numpy
import matplotlib.pyplot as plt

import TTC

### Some utility functions ###

def debug_print(val):
    print(val)

# a brutality
def force_int(val):
    try:
        return int(val)
    except:
        return 0


### Define finite mappings from slots (1--56) to dates, times, etc. ###

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


### Read CSVs ###

try:
    with open('preference.csv', encoding="utf-8") as f:
        reader = csv.reader(f)
        preferences = [list(map(force_int,row)) for row in reader]
        debug_print("Read preferences.csv")
except:
    with open('test.csv', encoding="utf-8") as f:
        reader = csv.reader(f)
        preferences = [list(map(force_int,row)) for row in reader]
        debug_print("Read test.csv")

try:
    with open('AllStudentList.csv', encoding="utf-8") as f:
        reader = csv.reader(f)
        student_list = [row for row in reader]
        student_map = {}
        for student in student_list:
            student_map[force_int(student[7])] = {
                "name":student[12],
                "barcode":student[22],
                "original_date":student[19],
                "original_time":student[20],
            }
        debug_print("Read AllStudentList.csv")
except:
    student_map = {}


### Keys for sorting the input (list of persons) ###

# a lexicographic key coupling the following criteria
# 1. those who does not necessarily need an exchange is to be placed
#    in the latter part of the sorted list
# 2. those who offer less options of exchange should appear sooner
def matching_difficulty(row):
    # `row` lists the exchangable slots offered by a person.
    # We first peek the value at the diagonal location:
    # this value being 0 or 1 means that this person
    # can be happy even without any change.
    # We are going to partition the sorted list into two and place such persons
    # in the latter part, hoping that the TTC algorithm be less likely to
    # hit them when searching for a cycle.
    # We should check if this strategy really works for the current algorithm,
    # which is a simple depth-first search (see TTC.py).
    b = 1 if row[row[0]] <= 2 else 0
    # Next, we count the number of offered slots by this person.
    # This is the second component of the key returned by this function,
    # rendering the sorted list increasing in this count in each partitions.
    # NB: we do not differentiate between 1 (strong preference) and 2 (weak) here.
    n = sum(map(lambda x: 1 if x <= 2 else 0, row[1:]))
    return b,n
def sort_pref(pref):
    return sorted(pref, key=matching_difficulty)

# a random key used for shuffling
def shuffling_key(row):
    return random.randint(1,1000000)
def shuffle_pref(pref, seed=100):
    random.seed(seed)
    return sorted(pref, key=shuffling_key)


### Preprocess the list according to the command-line ###

feedback_mode = False

args = sys.argv[1:]
if len(args) > 0:
    debug_print("Processing the arguments:")
while len(args) > 0:
    a = args.pop(0)
    if a == "shuffle":
        try:
            seed = int(args[0])
            args.pop(0)
        except:
            seed = 100
        preferences = shuffle_pref(preferences, seed)
        debug_print("- shuffled the list with seed={}".format(seed))
    elif a == "sort":
        preferences = sort_pref(preferences)
        debug_print("- sorted the list")
    elif a == "feedback":
        feedback_mode = True
        debug_print("- enabled the feedback loop")


### TTC and feedback ###

def print_TTC_result(all_cycles, residual):
    print(("TTC: {} cycles found. {} nodes unmatched, namely:\n{}").format(
        len(all_cycles),
        len(residual.nodes),
        residual.nodes
    ))

# Apply TTC once and print the intermediate result
# This function is just TTC.TTC() with printing some info about the result
# input: preferences
# output: all_cycles, residual
def run_TTC_once(pref):
    cycles, cycles2, residual = TTC.TTC(pref)
    all_cycles = cycles + cycles2
    print_TTC_result(all_cycles, residual)
    return all_cycles, residual

# Move to the top those rows whose indices are listed in residual.nodes
# input: preferences, residual (a graph whose nodes are (index+1) of preferences)
# output: preferences 
def feedback(pref, residual):
    pop_indices = reversed(sorted(residual.nodes))
    head = []
    for i in pop_indices:
        head.append(pref.pop(i-1))
    return head + pref

# repeat TTC and feedback while the number of residuals decreases
# input: preferences
# output: all_cycles, residual, preferences
def run_feedback_loop(pref):
    next_pref = pref.copy()
    all_cycles, residual = run_TTC_once(pref)
    invariant = len(pref)
    next_pref = feedback(next_pref, residual)
    new_cycles, new_cycles2, new_residual = TTC.TTC(next_pref)
    while len(new_residual.nodes) < len(residual.nodes):
        all_cycles = new_cycles + new_cycles2
        residual = new_residual
        print("\nFeeding back..\n")
        print_TTC_result(all_cycles, residual)
        next_pref = feedback(next_pref, residual)
        new_cycles, new_cycles2, new_residual = TTC.TTC(next_pref)
    return all_cycles, residual, next_pref


### afterTTC.csvファイルの作成 ###

# run TTC once or multiple times depending on `feedback_mode`
if feedback_mode:
    all_cycles, residual, preferences = run_feedback_loop(preferences)
else:
    all_cycles, residual = run_TTC_once(preferences)

# collect all edges
cycles_or_points = []
for cycle in all_cycles:
    cycles_or_points += cycle
# and also the isolated points, represented by virtual edges of the form `[j, -1]`
for j in residual.nodes:
    cycles_or_points.append([j, -1])
# then sort them lexicographically
cycles_or_points.sort()

g = open('afterTTC.csv', 'w', encoding="utf-8")

for i, applicant in enumerate(preferences):
    try:
        student_ID = applicant[58]
        student = student_map[student_ID]
        g.write(student["barcode"] + ','
                + str(student_ID) + ','
                + student["name"] + ','
                + student["original_date"] + ','
                + student["original_time"] + ',')
    except:
        g.write('')
    # applicant No.i の, 交換前のスロットを書き込む
    slot = applicant[0]
    # write 日付, time, min
    g.write(day_of_slot[slot])
    g.write(time_of_slot[slot])
    g.write(':')
    g.write('{:02}'.format(minute_of_slot[slot]))
    # write delimiters
    g.write(',' + '->' + ',')

    # applicant No.i の交換が成立した場合, 交換後のスロットを書き込む
    node_or_failure = cycles_or_points[i][1]
    if node_or_failure != -1:
        newslot = preferences[node_or_failure - 1][0]
        g.write(day_of_slot[newslot])
        g.write(time_of_slot[newslot])
        g.write(':')
        g.write('{:02}'.format(minute_of_slot[newslot]))
        g.write(',' + str(node_or_failure) + '\n')
    else:
        g.write('no match' + '\n')

g.close()


### Try to plot a histogram of the cycles ###

try:
    sizes = list(map(len, all_cycles))
    sizes.sort()
    largest = sizes[-1]
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(sizes, bins=numpy.arange(largest)+1.5, range=(1.5,largest+3.5))
    ax.set_xticks(range(largest+1))
    ax.set_yticks(n)
    plt.title("The distribution of the sizes of the cycles found")
    plt.show()
except:
    pass

