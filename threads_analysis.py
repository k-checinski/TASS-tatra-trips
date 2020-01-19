import json
import os


def all_threads(path):
    threads = list()
    for file in os.listdir(path):
        if file.endswith('.json'):
            with open(os.path.join(path, file), 'r') as json_file:
                threads.append(json.load(json_file))
    return threads

