from collections import namedtuple

import utils.approx_equal as approx_equal


Allocation = namedtuple("Allocation", ["cat", "perc"])


class AllocationSet:
    def __init__(self, allocations):
        self.map = dict(allocations)
        assert approx_equal.approx_equal(sum(self.map.values()), 1.0)


def compare_allocation_sets(goal, real, total_value=100.0):
    assert len(goal.map) == len(real.map)
    for cat in sorted(goal.map.keys()):
        assert cat in real.map

        g = goal.map[cat]
        r = real.map[cat]
        d = r - g
        nd = d / g if g != 0.0 else 0.0
        v = abs(d) * total_value
        action = "Remove" if d > 0.0 else "Add"

        print(
            "%-20s Goal: %5.1f%% | Real: %5.1f%% | Diff: %7.2f%%    %6s R$ %9.2f"
            % (cat.name, g * 100.0, r * 100.0, nd * 100.0, action, v)
        )


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

    tuple_list = []
    for sec in goal:
        g = goal[sec]
        r = real[sec]
        d = r - g
        nd = d / g if g != 0.0 else 0.0
        v = abs(d) * total_value

        tuple_list.append((sec, g, r, d, nd, v))

    sorted_tuples = sorted(
        tuple_list, reverse=True, key=lambda x: (abs(x[4]), abs(x[5]))
    )

    for i in sorted_tuples:
        (sec, g, r, d, nd, v) = i
        if g == r == 0.0:
            continue
        print(
            "%-15s Goal: %6.2f%% | Real: %6.2f%% | Diff: %7.2f%%    %4s R$ %9.2f"
            % (sec, g * 100.0, r * 100.0, nd * 100.0, "Sell" if d > 0.0 else "Buy", v)
        )
