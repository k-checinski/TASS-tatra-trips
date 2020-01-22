import collections
import math

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from threads_analysis import all_threads
from user import User


def build_users_graph():
    threads = all_threads('resources/threads/')
    user_graph = nx.DiGraph()
    for thread in threads:
        thread_info = thread['thread_info']
        author_name = thread_info['author']
        answers_num = thread_info['answers_num']
        title = thread_info['title']

        user = next((user_graph.nodes[x]['dict_attr'] for x in user_graph.nodes if x == author_name), None)

        if user is None:
            user = User(author_name)
            user_graph.add_node(author_name, dict_attr=user)

        user.create_thread(title, answers_num)

        for answer in thread['answers']:
            replier_name = answer['author']['name']
            replier = next((user_graph.nodes[x]['dict_attr'] for x in user_graph.nodes if x == replier_name), None)

            if replier is None:
                replier = User(replier_name)
                user_graph.add_node(replier_name, dict_attr=replier)

            replier.create_post()
            if author_name != replier_name:
                if not user_graph.has_edge(replier_name, author_name):
                    user_graph.add_edge(replier_name, author_name, weight=1)
                else:
                    user_graph.edges[replier_name, author_name]['weight'] += 1

    return user_graph


def draw_graph(graph, with_labels=False):
    pos = nx.spring_layout(graph)
    nx.draw_networkx(graph, node_size=40, alpha=0.8, with_labels=False, font_size=8, pos=pos)

    if with_labels:
        labels = dict((n, n) for n, d in graph.nodes(data=True))
        pos_higher = {}

        y_off = 0.05  # offset on the y axis
        x_off = -0.05  # offset on the x axis

        for k, v in pos.items():
            pos_higher[k] = (v[0] + x_off, v[1] + y_off)
        nx.draw_networkx_labels(graph, pos_higher, labels, font_size=8)

    plt.show()


def draw_degree_histogram(graph):
    degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)
    title = 'Histogram stopni wierzchołków'
    y_label = 'Liczba wierzchołków o danym stopniu'
    x_label = 'Stopień wierzchołka'
    plot_histogram(degree_sequence, 2, title, x_label, y_label)


def draw_in_degree_histogram(graph):
    degree_sequence = sorted([d for n, d in graph.in_degree()], reverse=True)
    title = 'Histogram stopni wchodzących wierzchołków'
    y_label = 'Liczba wierzchołków o danym stopniu wchodzącym'
    x_label = 'Stopień wchodzący wierzchołka'
    plot_histogram(degree_sequence, 2, title, x_label, y_label)


def draw_out_degree_histogram(graph):
    degree_sequence = sorted([d for n, d in graph.out_degree()], reverse=True)
    title = 'Histogram stopni wychodzących wierzchołków'
    y_label = 'Liczba wierzchołków o danym stopniu wychodzącym'
    x_label = 'Stopień wychodzący wierzchołka'
    plot_histogram(degree_sequence, 2, title, x_label, y_label)


def draw_edges_weights_histogram(graph):
    weights_sequence = sorted([graph.get_edge_data(*edge)['weight'] for edge in graph.edges], reverse=True)
    title = 'Histogram wag powiązań (krawędzi) pomiędzy autorami'
    y_label = 'Liczba krawędzi o danej wadze'
    x_label = 'Waga krawędzi'
    plot_histogram(weights_sequence, 20, title, x_label, y_label)


def show_activity_of_users_with_no_threads(graph):
    not_commented_users = [(node, graph.nodes[node[0]]['dict_attr'].threads_number)
                           for node in graph.in_degree if node[1] == 0]
    users_with_no_threads = [user[0][0] for user in not_commented_users if user[1] == 0]

    degree_sequence = sorted([node[1] for node in graph.out_degree if node[0] in users_with_no_threads], reverse=True)

    title = 'Histogram aktywności użytkowników, którzy nie stworzyli żadnego własnego wątku'
    y_label = 'Liczba wierzchołków o danym stopniu'
    x_label = 'Liczba użytkowników na których posty odpowiedziano'
    plot_histogram(degree_sequence, 2, title, x_label, y_label)


def plot_histogram(sequence, y_step, title, x_label, y_label):
    sequence_count = collections.Counter(sequence)
    item_value, cnt = zip(*sequence_count.items())
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.set_xticks([d for d in item_value if (d - 1) not in item_value or d % 2 != 0])  # if two labels in a row should
    # be visible, remove the second one if even
    plt.yticks(np.arange(1, max(cnt), y_step))
    plt.bar(item_value, cnt, width=1.0, color='b')
    plt.title(title)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.show()


# returns users to whose threads commented the biggest group of other users
def get_most_commented_users(graph):
    max_in_degrees = sorted(set([node[1] for node in graph.in_degree]), reverse=True)
    popular_users = dict()
    popular_users['top1'] = [(node, graph.nodes[node[0]]['dict_attr'].threads_number)
                             for node in graph.in_degree if node[1] == max_in_degrees[0]]
    popular_users['top2'] = [(node, graph.nodes[node[0]]['dict_attr'].threads_number)
                             for node in graph.in_degree if node[1] == max_in_degrees[1]]
    popular_users['top3'] = [(node, graph.nodes[node[0]]['dict_attr'].threads_number)
                             for node in graph.in_degree if node[1] == max_in_degrees[2]]

    return popular_users


# returns 3 tuples (author, commenter, how_many_times) representing edge and its weight with the highest weight value
def get_most_important_edges(graph):
    max_edge_weights = sorted([graph.get_edge_data(*edge)['weight'] for edge in graph.edges], reverse=True)
    popular_edges = dict()
    popular_edges['top1'] = [(edge, graph.get_edge_data(*edge)['weight'])
                             for edge in graph.edges if graph.get_edge_data(*edge)['weight'] == max_edge_weights[0]]
    popular_edges['top2'] = [(edge, graph.get_edge_data(*edge)['weight'])
                             for edge in graph.edges if graph.get_edge_data(*edge)['weight'] == max_edge_weights[1]]
    popular_edges['top3'] = [(edge, graph.get_edge_data(*edge)['weight'])
                             for edge in graph.edges if graph.get_edge_data(*edge)['weight'] == max_edge_weights[2]]

    return popular_edges


# returns users who commented on threads of biggest other users group
def get_most_commenting_users(graph):
    max_out_degrees = sorted(set([node[1] for node in graph.out_degree]), reverse=True)
    popular_users = dict()
    popular_users['top1'] = [node for node in graph.out_degree if node[1] == max_out_degrees[0]]
    popular_users['top2'] = [node for node in graph.out_degree if node[1] == max_out_degrees[1]]
    popular_users['top3'] = [node for node in graph.out_degree if node[1] == max_out_degrees[2]]

    return popular_users


# returns users on whose threads no one commented
def get_lonely_users(graph):
    lonely_users = [(node, graph.nodes[node[0]]['dict_attr'].threads_number)
                    for node in graph.degree if node[1] == 0]
    return lonely_users


# calculates user(v) authority as A(v) = ln[Σ w(Eu1v)] + ln[Σ w(Evu2)]). If an argument of logarithm is equal to 0 then
# is replaced with 1,as ln(1) = 0. [Σ w(Eu1v)] is the sum of weights of all edges, which end in v and start in u1
# (how many people commented on user threads). The other sum [Σ w(Evu2)] is the sum of weights of all edges, which start
# in v and end in u2 (on how  many people's threads user commented)
def get_user_authority(graph, name):
    in_edges_weights = sum([graph.get_edge_data(*edge)['weight'] for edge in graph.in_edges if edge[1] == name])
    out_edges_weights = sum([graph.get_edge_data(*edge)['weight'] for edge in graph.in_edges if edge[0] == name])

    in_edges_weights = in_edges_weights if in_edges_weights != 0 else 1
    out_edges_weights = out_edges_weights if out_edges_weights != 0 else 1

    return math.log(in_edges_weights) + math.log(out_edges_weights)
