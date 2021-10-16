### ADT for a row in preference.csv ###
class PreferenceRow:
    def __init__(self, node_ID, slot, pref, student_ID = None):
        self.row = {
            "node_ID":node_ID,
            "slot":slot,
            "preferences":pref,
            "student_ID":student_ID,
        }
    def node_ID(self):
        return self.row["node_ID"]
    def slot(self):
        return self.row["slot"]
    def preferences(self):
        return self.row["preferences"]
    def student_ID(self):
        return self.row["student_ID"]

    # the set of slot indexes that is marked maru (== 1; strongly preferred)
    # or sankaku (== 2; weakly preferred)
    def maru_slots(self):
        return {x[0]+1 for x in filter(lambda x: x[1] == 1,
                                     enumerate(self.preferences()))}
    def sankaku_slots(self):
        return {x[0]+1 for x in filter(lambda x: x[1] == 2,
                                     enumerate(self.preferences()))}
    def preferred_slots(self):
        return self.maru_slots() | self.sankaku_slots()

### Operations on a list of rows ###

## Misc. utilities ##

# the index of the row containing a given node ID
def row_index_of_node_ID(pref_matrix, node_ID):
    i, row = next(filter(lambda i_row: i_row[1].node_ID() == node_ID,
                         enumerate(pref_matrix)))
    return i

# the row containing a given node ID
def row_of_node_ID(pref_matrix, node_ID):
    return next(filter(lambda row: row.node_ID() == node_ID, pref_matrix))


## Sorting ##

# a lexicographic sorting that couples the following criteria
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
    preferred = row.preferred_slots()
    b = 1 if row.slot() in preferred else 0
    # Next, we count the number of offered slots by this person.
    # This is the second component of the key returned by this function,
    # rendering the sorted list increasing in this count in each partitions.
    # NB: we do not differentiate between 1 (strong preference) and 2 (weak) here.
    n = len(preferred)
    return b,n
def sort_pref(pref_matrix):
    return sorted(pref_matrix, key=matching_difficulty)

# a random key used for shuffling
def shuffle_pref(pref_matrix, seed=100):
    newmatrix = pref_matrix.copy()
    random.seed(seed)
    random.shuffle(newmatrix)
    return newmatrix

# (for printing) sort back according to node_ID
def sort_for_printer(pref_matrix):
    return sorted(pref_matrix, key=lambda row: row.node_ID())
