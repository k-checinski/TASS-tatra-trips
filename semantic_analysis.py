import json
import morfeusz2


def load_semantic_dict(path):
    with open(path, 'r') as file:
        content = json.load(file)
    sem_dict = dict()
    for row in content:
        sem_dict[row['name']] = row['weight']
    return sem_dict


def lemmas_list(analysis_result):
    lemmas = []
    last_index = None
    last_pos_elements = set()
    for record in analysis_result:
        index = record[0]
        if index != last_index:
            last_index = index
            if len(last_pos_elements) != 0:
                lemmas.append(list(last_pos_elements))
            last_pos_elements.clear()
        element = record[2][1]
        element = element.split(':')[0]
        last_pos_elements.add(element)
    if len(last_pos_elements) != 0:
        lemmas.append(list(last_pos_elements))
    return lemmas
