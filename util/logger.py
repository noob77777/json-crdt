import logging

from util.command_parser import CommandLineArgs


class Logger:
    # simple file logger for operations and debugging

    def __init__(self):
        self.cli = CommandLineArgs()
        FORMAT = '%(asctime)s %(message)s'
        logging.basicConfig(filename="operations-" + self.cli.get("name") + ".log",
                            format=FORMAT, level=logging.INFO)
        self.logger = logging.getLogger()

    def info(self, *args):
        self.logger.info(
            " * " + self.cli.get("name") + " :: " + " ".join(list(map(str, args))))
