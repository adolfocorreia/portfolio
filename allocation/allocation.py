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


def compare_securities_allocation(goal, real, total_value=100.0):
    diff1 = set(goal.keys()) - set(real.keys())
    diff2 = set(real.keys()) - set(goal.keys())
    for i in diff1:
        real[i] = 0.0
    for i in diff2:
        goal[i] = 0.0

    assert len(goal) == len(real)
    assert approx_equal.approx_equal(sum(goal.values()), 1.0)
    assert approx_equal.approx_equal(sum(real.values()), 1.0)

    for sec in goal:
        g = goal[sec]
        r = real[sec]
        d = r-g
        nd = d/g
        v = abs(d) * total_value

        print sec
        print "Goal: %5.2f%% | Real: %5.2f%% | Diff: %7.2f%%" \
            % (g*100.0, r*100.0, nd*100.0)
        if d < 0.0:
            print "    -    Add R$ %8.2f to balance" % v
        elif d > 0.0:
            print "    - Remove R$ %8.2f to balance" % v
        else:
            print "    - Perfect! No need to balance"
