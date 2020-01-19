class User:
    def __init__(self, name):
        self.name = name
        self.threads_number = 0
        self.posts_number = 0
        self.thread_titles = list()
        self.replies_number = 0

    def create_thread(self, thread_name, answers_num):
        self.threads_number += 1
        self.replies_number += answers_num - 1
        self.thread_titles.append(thread_name)

    def create_post(self):
        self.posts_number += 1
