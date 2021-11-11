import sys

from util.command_parser import CommandLineArgs


class LamportCounter:
    # generate globally unique operation ids (node_id, counter)

    def __init__(self):
        self.cli = CommandLineArgs()
        self.id = self.cli.get("name")
        self.counter = 0

    def __str__(self):
        return "( " + self.id + ", " + str(self.counter) + " )"

    def set(self, counter):
        self.counter = counter

    def increment(self):
        self.counter += 1

    # returns a copy
    def get(self):
        ct = LamportCounter()
        ct.id = self.id
        ct.counter = self.counter
        return ct

    # comparators
    # counter value is given first preference
    # in case counter is same (concurrent operation) node_id is used
    # this gives a arbitary but deterministic ordering of operations

    def __gt__(self, other):
        if self.counter > other.counter:
            return True
        elif self.counter < other.counter:
            return False
        else:
            return self.id > other.id

    def __lt__(self, other):
        if self.counter < other.counter:
            return True
        elif self.counter > other.counter:
            return False
        else:
            return self.id < other.id
