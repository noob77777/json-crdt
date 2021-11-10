import logging


class Logger:
    def __init__(self):
        FORMAT = '%(asctime)s %(message)s'
        logging.basicConfig(format=FORMAT)
        self.logger = logging.getLogger('default')

    def debug(self, message):
        self.logger.debug(message)
