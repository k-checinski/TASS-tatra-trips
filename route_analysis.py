import copy
import json
import os
from math import sqrt, fabs, sin, atan2, cos
from typing import Set, List

import matplotlib.pyplot as plt
import morfeusz2
import numpy as np

from pl_stemmer import stem


def is_sufficient(prepared_tuple):
    part_of_speech = prepared_tuple[1].split(':')[0]
    return part_of_speech in ['ign']


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
                                 'coords': (term['latitude'], term['longitude'])})
    return prepared_objects


def process_word(word_result):
    info = [list(w[2]) for w in word_result]
    for result_tuple in info:
        if result_tuple[2] == 'ign':
            result_tuple[1] = stem(result_tuple[1])
    return info


def find_special_words(text_position):
    if 'przez' in text_position:
        return ['przez']
    return None


def swap_elements(route, window=2):
    for i, objs in enumerate(route[1:-1]):
        i = i + 1
        if len(objs) != 1 or objs[0][0]['name'] != ['przez']:
            continue
        mid = objs[0][1]
        a = mid - window
        b = mid + window
        objs_before = None
        if route[i - 1][0][1] >= a:
            objs_before = route[i - 1]
        objs_after = None
        if route[i + 1][0][1] <= b:
            objs_after = route[i + 1]
        if objs_before is not None and objs_after is not None:
            print(objs_before, 'przez', objs_after)
            route[i - 1] = objs_after
            route[i + 1] = objs_before
    final_route = []
    for objs in route:
        if objs[0][0]['name'] != ['przez']:
            final_route.append([o[0] for o in objs])
    return final_route


def prepare_text(text: str, morf: morfeusz2.Morfeusz) -> List[Set[str]]:
    analysed_text = morf.analyse(text)
    pos = 0
    sets = []
    current_set = set()
    for morf_tuple in analysed_text:
        part_of_speech = morf_tuple[2][2].split(':')[0]
        if part_of_speech in ['interj', 'conj', 'part', 'siebie',
                              'fin', 'bedzie', 'aglt', 'impt', 'imps',
                              'inf', 'winien', 'pred', 'comp',
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
    special_word = find_special_words(text_lemmas_sets[start_pos])
    if special_word is not None:
        matches.append(({'name': special_word}, 1, start_pos))
        return matches
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
            matches.append((copy.deepcopy(object), match_count, start_pos))
    return matches


def dist(a, b):
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def dist_obj(a, b):
    a_pos = a['coords']
    b_pos = b['coords']
    return dist(a_pos, b_pos)


def dist_obj_km(a, b):
    return (dist_obj(a, b) / 3600) * 40000


def true_dist(a, b):
    d1 = fabs(a[0] - b[0])
    d2 = fabs(a[1] - b[1])
    a = sin(d1 / 2) ** 2 + cos(a[0]) * cos(b[0]) * (sin(d2 / 2) ** 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = 6371 * c
    return d


def filter_variants(route):
    if len(route) == 0:
        return []
    if len(route) == 1:
        return [route[0][0]]
    init_obj, init_dist = route[0][0], dist_obj(route[0][0], route[1][0])
    for a in route[0]:
        for b in route[1]:
            ab_dist = dist_obj(a, b)
            if ab_dist < init_dist:
                init_dist = ab_dist
                init_obj = a
    filtered_route = [init_obj]
    for elem in route[1:]:
        if len(elem) == 1:
            filtered_route.append(elem[0])
            continue
        distances = [dist_obj(filtered_route[-1], variant) for variant in elem]
        nearest = elem[np.argmin(distances)]
        filtered_route.append(nearest)
    return filtered_route


def filter_far_objects(route, min_filtering_distance=10000.0):
    if len(route) == 0:
        return []
    if len(route) <= 2:
        return route
    filtered_route = []
    start_pos = 1
    if dist_obj(route[0], route[1]) > dist_obj(route[0], route[2]):
        filtered_route.append(route[0])
    else:
        filtered_route.append(route[1])
        start_pos = 2
    filtered_route = [route[0]]
    for a, b in zip(route[start_pos:], route[start_pos + 1:]):
        a_coords = a['coords']
        b_coords = b['coords']
        prev_coords = filtered_route[-1]['coords']
        a_prev_dist = dist(prev_coords, a_coords)
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
               far_objects_filtering_dist=0.0, splitting_min_dist=None):
    pos = 0
    morf = morfeusz2.Morfeusz()
    sets = prepare_text(text, morf)
    route = []
    while pos < len(sets):
        matches = find_next_object(sets, pos, objects_dict)
        if len(matches) == 0:
            pos += 1
            continue
        objects, lengths, positions = zip(*matches)
        max_length = max(lengths)
        pos += max_length
        route.append([(m[0], m[2]) for m in matches if m[1] == max_length])
    route = swap_elements(route)
    route = filter_variants(route)
    remove_needless_fields(route)
    if far_objects_filtering_dist > 0:
        route = filter_far_objects(route, far_objects_filtering_dist)
    if duplicates_filtering_window != 0:
        route = filter_duplicates(route, duplicates_filtering_window)
    route = filter_duplicates(route, 1)
    if splitting_min_dist is not None:
        route = split_route(route, splitting_min_dist)
    return route


def remove_needless_fields(route):
    for obj in route:
        del obj['keywords']
        del obj['type']


def split_route(route, max_dist):
    if len(route) <= 1:
        return [route]
    subroutes = []
    new_subroute = [route[0]]
    for object in route[1:]:
        d = dist_obj(new_subroute[-1], object)
        if d > max_dist:
            subroutes.append(new_subroute)
            new_subroute = []
        new_subroute.append(object)
    subroutes.append(new_subroute)
    return subroutes


def draw_route(objects):
    xs = []
    ys = []
    names = []
    for obj in objects:
        coords = obj['coords']
        xs.append(coords[1])
        ys.append(coords[0])
        names.append(obj['name'])
    plt.plot(xs, ys, '-o')
    for x, y, label in zip(xs, ys, names):
        plt.annotate(label,  # this is the text
                     (x, y),  # this is the point to label
                     textcoords="offset points",  # how to position the text
                     xytext=(0, 10),  # distance from text to points (x,y)
                     ha='center')


def process_all_threads(duplicates_filtering_window=3, far_objects_filtering_dist=0.015,
                        splitting_min_dist=0.056, threads_dir='threads'):
    with open('resources/geo.json', 'r') as file:
        objs = json.load(file)
    prep = prepare_objects(objs)
    routes = []
    filenames = os.listdir(threads_dir)
    processed_filenames = []
    # filenames = ['376_80.json']
    for i, filename in enumerate(filenames):
        print(f'{i+1}/{len(filenames)}:\t{filename}')
        if not filename.endswith('.json'):
            continue
        with open(os.path.join('threads', filename)) as file:
            thread = json.load(file)
        if len(thread['answers']) == 0:
            print('EMPTY THREAD')
            continue
        text = thread['answers'][0]['content']
        route = find_route(text, prep, duplicates_filtering_window, far_objects_filtering_dist, splitting_min_dist)
        routes.append(route)
        processed_filenames.append(filename)
    return routes, processed_filenames


def sections_length(routes):
    sections_lengths = []
    for route in routes:
        for a, b in zip(route, route[1:]):
            sections_lengths.append(dist_obj(a, b))
    return sections_lengths


def draw_routes(routes, names):
    for route, name in zip(routes, names):
        if isinstance(route[0], list):
            for subroute in route:
                draw_route(subroute)
        else:
            draw_route(route)
        plt.title(name)
        plt.savefig(name + '.png')
        plt.clf()


if __name__ == '__main__':
    routes, filenames = process_all_threads()
    draw_routes(routes, [name.split('.')[0] for name in filenames])
