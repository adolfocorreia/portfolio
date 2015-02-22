from collections import namedtuple

import utils.approx_equal as approx_equal


Allocation = namedtuple("Allocation", ["cat", "perc"])


class AllocationSet:

    def __init__(self, allocations):
        self.map = dict(allocations)
        assert approx_equal.approx_equal(sum(self.map.values()), 1.0)


def compare_allocation_sets(goal, real, total_value=100.0):
    assert len(goal.map) == len(real.map)
    for cat in goal.map.keys():
        assert cat in real.map

        g = goal.map[cat]
        r = real.map[cat]
        d = r-g
        nd = d/g
        v = abs(d) * total_value

        print cat
        print "Goal: %5.2f | Real: %5.2f | Diff: %5.2f" % (g, r, nd)
        if d < 0.0:
            print "-    Add R$ %8.2f to balance" % v
        elif d > 0.0:
            print "- Remove R$ %8.2f to balance" % v
        else:
            print "- Perfect! No need to balance"

        print
