import sys


class CommandLineArgs:
    # command line argument parser

    def __init__(self):
        self.data = dict()
        for i in range(len(sys.argv)):
            if sys.argv[i] == "-p" or sys.argv[i] == "--port":
                self.data["port"] = int(sys.argv[i + 1])
            if sys.argv[i] == "--name":
                self.data["name"] = sys.argv[i + 1]

    def get(self, key):
        return self.data[key]
