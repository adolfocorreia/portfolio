import re
import operator
from collections import defaultdict
from functools import reduce


class SecuritySelector:
    def __init__(self, num_of_secs=0, ignore_secs=[], regex_rules=[]):
        self.num_of_secs = num_of_secs
        self.ignore_secs = ignore_secs
        self.regex_rules = regex_rules

    def select_securities(self, securities):
        # 0. Get key-value tuples iterator from securities dict
        secs = securities.items()

        # 1. Remove ignored securities
        secs = [x for x in secs if x[0] not in self.ignore_secs]

        # 2. Apply regexp rules on security names
        for rule in self.regex_rules:
            regex = re.compile(rule[0])
            secs = [(regex.sub(rule[1], x[0]), x[1]) for x in secs]

        # 2.1. Join same security entries
        joined_secs = defaultdict(float)
        for sec in secs:
            joined_secs[sec[0]] += sec[1]
        secs = list(joined_secs.items())

        # 3. Sort and remove least significant securities
        secs = sorted(secs, key=operator.itemgetter(1), reverse=True)
        if self.num_of_secs != 0:
            secs = secs[: self.num_of_secs]

        # 4. Normalize percentages
        total = reduce(operator.add, map(lambda x: x[1], secs))
        secs = [(x[0], x[1] / total) for x in secs]

        return dict(secs)


def join_securities(securitiesA, securitiesB, num_of_secs=20):
    # 0. Get key-value tuples iterators from securities dicts
    secsA = securitiesA.items()
    secsB = securitiesB.items()

    # 1. Join same security entries
    joined_secs = defaultdict(float)
    for sec in secsA:
        joined_secs[sec[0]] += sec[1]
    for sec in secsB:
        joined_secs[sec[0]] += sec[1]
    secs = joined_secs.items()

    # 2. Sort and remove least significant securities
    secs = sorted(secs, key=operator.itemgetter(1), reverse=True)
    if num_of_secs != 0:
        secs = secs[:num_of_secs]

    # 3. Normalize percentages
    total = reduce(operator.add, map(lambda x: x[1], secs))
    secs = [(x[0], x[1] / total) for x in secs]

    return dict(secs)
