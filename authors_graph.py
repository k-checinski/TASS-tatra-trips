from user import User
from threads_analysis import all_threads
import networkx as nx
import matplotlib.pyplot as plt


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
                if not user_graph.has_edge(replier_name, author_name ):
                    user_graph.add_edge(replier_name, author_name, weight=1)
                else:
                    user_graph.edges[replier_name, author_name]['weight'] += 1

    nx.draw(user_graph)
    plt.show()
    return user_graph