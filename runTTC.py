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

import preference as P
import TTC

### Settings

## this constant is needed for read_row()
number_of_slots = 51

## Define finite mappings from slots (1--51) to dates, times, etc. ###

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

# 日付: 1~18:10/19, 19~36:10/20, 37~51:10/22
days = [
    ('10/19 ', CI(1,18)),
    ('10/20 ', CI(19,36)),
    ('10/22 ', CI(37,51)),
]
day_of_slot = expand_to_dict(days)

# 時: (1~6 or 19~24 or 37~42):14,
# (7~12 or 25~30 or 43~48):15,
# (13~18 or 31~36 or 49~51):16,
times = [
    ('14', CI(1,6) + CI(19,24) + CI(37,42)),
    ('15', CI(7,12) + CI(25,30) + CI(43,48)),
    ('16', CI(13,18) + CI(31,36) + CI(49,51)),
#    ('17', [37,56]),
]
time_of_slot = expand_to_dict(times)

# 分:slot が (((6で割った余り) + 5) を 6 で割った余り)×10
minute_of_slot = {}
for slot in CI(1,51):
    minute_of_slot[slot] = ((slot+5)%6) * 10
#for slot in CI(38,56):
#    minute_of_slot[slot] = ((slot+4)%6) * 10


### Read CSVs ###

# distinguish normal printer and debug printer
def debug_print(val):
    print(val)

# a brutality
def force_int(val):
    try:
        return int(val)
    except:
        return 0

# CSV row to PreferenceRow
def read_row(row_index, csv_row, number_of_slots):
    int_csv_row = list(map(force_int, csv_row))
    slot = int_csv_row[0]
    pref = int_csv_row[1:number_of_slots+1]
    try:
        student_ID = int_csv_row[number_of_slots+2]
    except:
        student_ID = None
    return P.PreferenceRow(row_index, slot, pref, student_ID)

# CSV reader
def read_pref_csv():
    try:
        with open('preference.csv', encoding="utf-8") as f:
            reader = enumerate(csv.reader(f))
            pref_matrix = [read_row(i_row[0], i_row[1], number_of_slots)
                           for i_row in reader]
            debug_print("Read preferences.csv")
    except:
        with open('test.csv', encoding="utf-8") as f:
            reader = enumerate(csv.reader(f))
            pref_matrix = [read_row(i_row[0], i_row[1], number_of_slots)
                           for i_row in reader]
            debug_print("Read test.csv")
    return pref_matrix

# printf-test if the file is correctly read
def test_read_pref_csv(pref_matrix):
    for row in pref_matrix:
        s = "{}; {}; {}; pref={}".format(
            row.node_ID(), row.slot(), row.student_ID(), rw.preferences())
        print(s)

# The reader for the auxiliary info of students
def read_student_list_csv():
    try:
        with open('2ndAllStudentList2.csv', encoding="utf-8") as f:
            reader = csv.reader(f)
            student_list = [row for row in reader]
            student_map = {}
            # a mapping from 学籍番号 to other personal data
            # student[7] is the 学籍番号 in AllStudentList.csv
            for student in student_list:
                student_map[force_int(student[8])] = {
                    "name":student[6],
                    "barcode":student[16],
                    "original_date":student[13],
                    "original_time":student[14],
                }
            debug_print("Read 2ndAllStudentList2.csv")
    except:
        student_map = {}
    return student_map


### TTC and feedback ###

# Printer for the (intermediate) results
def print_TTC_result(all_cycles, residual):
    print(("TTC: {} cycles found. {} nodes unmatched, namely:\n{}").format(
        len(all_cycles),
        len(residual.nodes),
        sorted(residual.nodes)
    ))

# Apply TTC once and print the intermediate result
# This function is just TTC.TTC() with printing some info about the result
# input: pref_matrix
# output: all_cycles, residual
def run_TTC_once(pref_matrix):
    cycles, cycles2, residual = TTC.TTC(pref_matrix)
    all_cycles = cycles + cycles2
    print_TTC_result(all_cycles, residual)
    return all_cycles, residual

def node_IDs(pref_matrix):
    return [row.node_ID() for row in pref_matrix]

# Move to the top those rows whose indices are listed in residual.nodes
# input: pref_matrix, residual (a graph whose nodes are (index+1) of pref_matrix)
# output: pref_matrix 
def feedback(pref_matrix, residual):
    residual_row_indices = list(
        map(lambda ID: P.row_index_of_node_ID(pref_matrix, ID),
            residual.nodes))
    # remove residual rows backwards from the end of pref_matrix
    pop_indices = reversed(sorted(residual_row_indices))
    head = []
    for i in pop_indices:
        head.append(pref_matrix.pop(i))
    return head + pref_matrix

# repeat TTC and feedback while the number of residuals decreases
# input: pref_matrix
# output: all_cycles, residual, pref_matrix
def run_feedback_loop(pref_matrix):
    next_matrix = pref_matrix.copy()
    matrix = next_matrix.copy()
    all_cycles, residual = run_TTC_once(matrix)
    next_matrix = feedback(matrix, residual)
    new_cycles, new_cycles2, new_residual = TTC.TTC(next_matrix)
    while len(new_residual.nodes) < len(residual.nodes):
        all_cycles = new_cycles + new_cycles2
        residual = new_residual
        matrix = next_matrix.copy()
        print("\nFeeding back..\n")
        print_TTC_result(all_cycles, residual)
        next_matrix = feedback(next_matrix, residual)
        new_cycles, new_cycles2, new_residual = TTC.TTC(next_matrix)
    return all_cycles, residual, matrix


### Execute all and afterTTC.csvファイルの作成 ###

# read from the csv files
pref_matrix = read_pref_csv()
student_map = read_student_list_csv()

# Preprocess the list according to the command-line #
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
        pref_matrix = P.shuffle_pref(pref_matrix, seed)
        debug_print("+ shuffled the matrix with seed={}".format(seed))
    elif a == "sort":
        pref_matrix = P.sort_pref(pref_matrix)
        debug_print("+ sorted the matrix")
    elif a == "feedback":
        feedback_mode = True
        debug_print("+ enabled the feedback loop")

# run TTC, once or multiple times depending on `feedback_mode`
if feedback_mode:
    all_cycles, residual, pref_matrix = run_feedback_loop(pref_matrix)
else:
    all_cycles, residual = run_TTC_once(pref_matrix)

# collect all edges into a mapping from nodes to lists of nodes
# Recall that an edge [A_ID, B_ID] means that B's slot is listed in A's preference
cycles_or_points = {row.node_ID() : [] for row in pref_matrix}
for cycle in all_cycles:
    for edge in cycle:
        cycles_or_points[edge[0]].append(edge[1])

# test if the generated cycles_or_points is consistent with pref_matrix
def test_cycles_or_points(cycles_or_points, pref_matrix):
    all_nodes = {row.node_ID() for row in pref_matrix}
    residual_nodes = set(residual.nodes)

    # cycles_or_points must have all nodes in pref_matrix as its domain
    assert set(cycles_or_points.keys()) == all_nodes

    for A in pref_matrix:
        A_ID = A.node_ID()
        A_to_which_nodes = cycles_or_points[A_ID]
        A_to_how_many_nodes = len(A_to_which_nodes)
        # each node may be mapped to at most one node
        # if the node is mapped to another,
        # the corresponding edge must exist in the original preference matrix
        if A_to_how_many_nodes == 1:
            B_ID = A_to_which_nodes[0]
            B_slot = P.row_of_node_ID(pref_matrix, B_ID).slot()
            A_prefs = A.preferred_slots()
            assert B_slot in A_prefs
        # if it is zero, node_ID must be in residuals
        elif A_to_how_many_nodes == 0:
            assert A_ID in residual_nodes
        else:
            assert False

# Run the above test before writing to afterTTC.csv:
# read the CSV again,
orig_pref_matrix = read_pref_csv()
# and test the cycles_or_points to it
test_cycles_or_points(cycles_or_points, orig_pref_matrix)
debug_print("Checked the consistency of the cycles")


# generate afterTTC.csv
g = open('afterTTC.csv', 'w', encoding="utf-8")

for A in P.sort_for_printer(pref_matrix):
    A_ID = A.node_ID()
    try:
        student_ID = A.student_ID()
        student = student_map[student_ID]
        g.write(student["barcode"] + ','
                + str(student_ID) + ','
                + student["name"] + ','
                + student["original_date"] + ','
                + student["original_time"] + ',')
    except:
        g.write('')
    # print A's ID
    g.write(str(A_ID) + ',')
    # write 日付, time, min
    A_slot = A.slot()
    g.write(day_of_slot[A_slot])
    g.write(time_of_slot[A_slot])
    g.write(':')
    g.write('{:02}'.format(minute_of_slot[A_slot]))
    # write delimiters
    g.write(',' + '->' + ',')

    # applicant No.i の交換が成立した場合, 交換後のスロットを書き込む
    node_or_failure = cycles_or_points[A_ID]
    if len(node_or_failure) == 1:
        B_ID = node_or_failure[0]
        B_slot = P.row_of_node_ID(pref_matrix, B_ID).slot()
        g.write(day_of_slot[B_slot])
        g.write(time_of_slot[B_slot])
        g.write(':')
        g.write('{:02}'.format(minute_of_slot[B_slot]))
        g.write(',' + str(B_ID) + '\n')
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

