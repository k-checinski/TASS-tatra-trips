import json


def load_semantic_dict(path):
    with open(path, 'r') as file:
        content = json.load(file)
    sem_dict = dict()
    for row in content:
        sem_dict[row['name']] = row['weight']
    return sem_dict