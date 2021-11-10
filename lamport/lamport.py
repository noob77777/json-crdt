import sys


class LamportCounter:
    def __init__(self):
        self.id = sys.argv[1]
        self.counter = 0

    def __str__(self):
        return "( " + self.id + ", " + str(self.counter) + " )"

    def set(self, counter):
        self.counter = counter

    def increment(self):
        self.counter += 1

    def get(self):
        ct = LamportCounter()
        ct.id = self.id
        ct.counter = self.counter
        return ct

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
