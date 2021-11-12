import json


class ConfigReader:
    # reads config params from config.json

    def __init__(self):
        f = open('config.json',)
        self.config = json.load(f)
        f.close()

    def get(self, key):
        return self.config[key]
