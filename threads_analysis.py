import json
import os


def all_threads(path):
    os.chdir("")
    threads = list()
    for file in os.listdir(path):
        if file.endswith('.json'):
            threads.append(json.load(file))
