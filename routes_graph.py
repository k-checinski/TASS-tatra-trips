import copy
import json
import os

import networkx as nx

from authors_graph import draw_graph, get_user_authority, build_users_graph
from route_analysis import prepare_objects, find_route
from sentiment_analysis import get_thread_sentiment_score


def add_route_to_graph(routes_graph, route, author_score, sentiment_score):
    object_info = dict()
    object_info['author_score'] = author_score
    object_info['sentiment_score'] = sentiment_score
    object_info['total_score'] = author_score + sentiment_score

    pos = 0
    for obj in route:
        if obj['name'] in routes_graph.nodes:
            routes_graph.nodes[obj['name']]['dict_attr']['sentiment_score'] += sentiment_score
            routes_graph.nodes[obj['name']]['dict_attr']['total_score'] += author_score + sentiment_score
            routes_graph.nodes[obj['name']]['dict_attr']['author_score'] += author_score
            print('node already in graph')
        else:
            object_info['coords'] = obj['coords']
            routes_graph.add_node(obj['name'], dict_attr=copy.deepcopy(object_info))

    for obj in route:
        next_obj = route[pos + 1] if pos < len(route) - 1 else None
        if next_obj is not None:
            routes_graph.add_edge(obj['name'], next_obj['name'])
        pos += 1


def build_routes_graph(threads_dir='resources/threads'):
    with open('resources/geo.json', 'r') as file:
        objs = json.load(file)
    prep = prepare_objects(objs)

    users_graph = build_users_graph()

    duplicates_filtering_window = 3
    far_objects_filtering_dist = 0.015
    splitting_min_dist = 0.056

    filenames = os.listdir(threads_dir)
    routes_graph = nx.Graph()
    for filename in filenames:
        if not filename.endswith('.json'):
            continue
        print(filename)
        with open(os.path.join('resources/threads', filename)) as file:
            thread = json.load(file)

        if len(thread['answers']) == 0:
            continue
        text = thread['answers'][0]['content']

        routes = find_route(text, prep, duplicates_filtering_window, far_objects_filtering_dist, splitting_min_dist)
        print(len(routes))
        author_name = thread['thread_info']['author']
        author_authority = get_user_authority(users_graph, author_name)
        sentiment_score = get_thread_sentiment_score(thread)
        if isinstance(routes[0], list):
            for subroute in routes:
                add_route_to_graph(routes_graph, subroute, author_score=author_authority,
                                   sentiment_score=sentiment_score)
        else:
            add_route_to_graph(routes_graph, subroute, author_score=author_authority,
                               sentiment_score=sentiment_score)

    draw_graph(routes_graph, with_labels=True)
    return routes_graph


def get_top_objects(graph):
    max_sentiment_scores = sorted(set([graph.nodes[node]['dict_attr']['sentiment_score'] for node in graph.nodes]),
                                  reverse=True)
    high_sentiment_objects = dict()
    high_sentiment_objects['top1'] = [node for node in graph.nodes if
                                      graph.nodes[node]['dict_attr']['sentiment_score'] == max_sentiment_scores[0]]
    high_sentiment_objects['top2'] = [node for node in graph.nodes if
                                      graph.nodes[node]['dict_attr']['sentiment_score'] == max_sentiment_scores[1]]
    high_sentiment_objects['top3'] = [node for node in graph.nodes if
                                      graph.nodes[node]['dict_attr']['sentiment_score'] == max_sentiment_scores[2]]

    return high_sentiment_objects


if __name__ == '__main__':
    x = build_routes_graph()
    print((get_top_objects(x)))
