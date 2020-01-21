from typing import Set, List
from math import sqrt

import numpy as np
import matplotlib.pyplot as plt

import morfeusz2
from pl_stemmer import stem


def is_sufficient(prepared_tuple):
    part_of_speech = prepared_tuple[1].split(':')[0]
    return part_of_speech in ['ign'] or 'nazwa_geograficzna' in prepared_tuple[2]


def prepare_objects(terms):
    morf = morfeusz2.Morfeusz()
    print(morf.dict_id())
    prepared_objects = []
    for term in terms:
        words = term['name'].split(' ')
        words_results = [morf.analyse(w) for w in words]
        prepared_words = []
        for word_result in words_results:
            info = process_word(word_result)
            prepared_result = [(w[1], w[2].split(':')[0], w[3]) for w in info]
            forms = set([r[0].split(':')[0].lower() for r in prepared_result])
            prepared_words.append((forms, any([is_sufficient(t) for t in prepared_result])))
        prepared_objects.append({'name': term['name'], 'keywords': prepared_words, 'type': term['type'],
                                 'latitude': term['latitude'], 'longitude': term['longitude']})
    return prepared_objects


def process_word(word_result):
    info = [list(w[2]) for w in word_result]
    for result_tuple in info:
        if result_tuple[2] == 'ign':
            result_tuple[1] = stem(result_tuple[1])
    return info


def prepare_text(text: str, morf: morfeusz2.Morfeusz) -> List[Set[str]]:
    analysed_text = morf.analyse(text)
    pos = 0
    sets = []
    current_set = set()
    for morf_tuple in analysed_text:
        part_of_speech = morf_tuple[2][2].split(':')[0]
        if part_of_speech in ['interj', 'conj', 'part', 'siebie',
                              'fin', 'bedzie', 'aglt', 'impt', 'imps',
                              'inf', 'winien', 'pred', 'prep', 'comp',
                              'interj', 'interp']:
            continue
        if morf_tuple[0] != pos:
            if len(current_set) != 0:
                sets.append(current_set)
                current_set = set()
            pos = morf_tuple[0]
        lemma = morf_tuple[2][1].split(':')[0]
        if part_of_speech == 'ign':
            lemma = stem(lemma)
        lemma = ''.join(c for c in lemma if c.isalnum())
        if len(lemma) > 0:
            current_set.add(lemma.lower())
    return sets


def find_next_object(text_lemmas_sets, start_pos, objects_dict):
    matches = []
    for object in objects_dict:
        current_pos = start_pos
        match_count = 0
        sufficient_matched = False
        for keyword in object['keywords']:
            overlap = not keyword[0].isdisjoint(text_lemmas_sets[current_pos])
            if overlap:
                match_count += 1
                if keyword[1]:
                    sufficient_matched = True
            current_pos += 1
            if current_pos >= len(text_lemmas_sets):
                break
        if match_count == len(object['keywords']) or sufficient_matched:
            matches.append((object, match_count))
    return matches


def dist(a, b):
    return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def get_coords(obj):
    return obj['latitude'], obj['longitude']


def filter_variants(route):
    if len(route) == 0:
        return []
    filtered_route = [route[0][0]]
    for elem in route[1:]:
        if len(elem) == 1:
            filtered_route.append(elem[0])
            continue
        prev_coords = get_coords(filtered_route[-1])
        distances = [dist(prev_coords, get_coords(variant)) for variant in elem]
        nearest = elem[np.argmin(distances)]
        filtered_route.append(nearest)
    return filtered_route


def filter_far_objects(route, min_filtering_distance=10000.0):
    if len(route) == 0:
        return []
    filtered_route = [route[0]]
    for a, b in zip(route[1:], route[2:]):
        a_coords = get_coords(a)
        b_coords = get_coords(b)
        prev_coords = get_coords(filtered_route[-1])
        a_prev_dist = dist(prev_coords, a_coords)
        print(a_prev_dist, a['name'], b['name'])
        if a_prev_dist < dist(prev_coords, b_coords) or a_prev_dist < min_filtering_distance:
            filtered_route.append(a)
    filtered_route.append(route[-1])
    return filtered_route


def filter_duplicates(route, window_size=1):
    if len(route) < window_size:
        return route
    filtered_route = route[:window_size]
    for object in route[window_size:]:
        if not object['name'] in [o['name'] for o in filtered_route[-window_size:]]:
            filtered_route.append(object)
    return filtered_route


def find_route(text, objects_dict, duplicates_filtering_window=0,
               far_objects_filtering_dist=0):
    pos = 0
    morf = morfeusz2.Morfeusz()
    sets = prepare_text(text, morf)
    route = []
    while pos < len(sets):
        matches = find_next_object(sets, pos, objects_dict)
        if len(matches) == 0:
            pos += 1
            continue
        objects, lengths = zip(*matches)
        max_length = max(lengths)
        pos += max_length
        route.append([m[0] for m in matches if m[1] == max_length])
    route = filter_variants(route)
    if far_objects_filtering_dist > 0:
        route = filter_far_objects(route, far_objects_filtering_dist)
    if duplicates_filtering_window != 0:
        route = filter_duplicates(route, duplicates_filtering_window)
    return route


def draw_route(objects):
    xs = []
    ys = []
    names = []
    for obj in objects:
        xs.append(obj['longitude'])
        ys.append(obj['latitude'])
        names.append(obj['name'])
    plt.plot(xs, ys, '-o')
    for x, y, label in zip(xs, ys, names):
        plt.annotate(label,  # this is the text
                     (x, y),  # this is the point to label
                     textcoords="offset points",  # how to position the text
                     xytext=(0, 10),  # distance from text to points (x,y)
                     ha='center')
    plt.show()


if __name__ == '__main__':
    import json
    with open('resources/geo.json', 'r') as file:
        objs = json.load(file)
    prep = prepare_objects(objs)
    with open('threads/19_4774.json') as file:
        thread = json.load(file)
    text = thread['answers'][0]['content']
    # text = "Wyruszyliśmy z Kuźnic, przez Dolinę Jaworzynki dotarliśmy do Murowańca i dalej nad Czarny Staw Gąsienicowy. " \
    # "Wdrapaliśmy się na Karb, zdobyliśmy Kościelec i zeszliśmy na Karb i drugą stroną wróciliśmy przez Murowaniec i Boczań do Kuźnic."
    print(text)
    route = find_route(text, prep)
    draw_route(route)

    for elem in route:
        print(elem)
    print('FILTERED')

    route = filter_duplicates(route, 1)
    draw_route(route)

    for elem in route:
        print(elem)
