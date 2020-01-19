import json
import morfeusz2
import sys
from typing import Dict, List


def load_sentiment_dict(path):
    with open(path, 'r') as file:
        content = json.load(file)
    sem_dict = dict()
    for row in content:
        sem_dict[row['name']] = row['weight']
    return sem_dict


def lemmas_list(analysis_result: list):
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


def position_sentiment_score(lemmas_group: List[str], sentiment_dict: Dict[str, int], verbose=False):
    value = max([int(sentiment_dict.get(lemma, "0")) for lemma in lemmas_group])
    if value != 0 and verbose:
        print(lemmas_group, value)
    return value


def sentiment_score(lemmas_list: List[List[str]], sentiment_dict: Dict[str, int], verbose=False):
    return sum([position_sentiment_score(lemmas_group, sentiment_dict, verbose) for lemmas_group in lemmas_list])


def answer_sentiment_score(text: str, sentiment_dict: Dict[str, int], morf: morfeusz2.Morfeusz, verbose=False):
    analysis = morf.analyse(text)
    lemmas = lemmas_list(analysis)
    return sentiment_score(lemmas, sentiment_dict, verbose)


def thread_sentiment_score(thread: dict, sentiment_dict: Dict[str, int], morf: morfeusz2.Morfeusz, verbose=False):
    answers = thread['answers']
    final_score = 0
    for answer in answers:
        score = answer_sentiment_score(answer['content'], sentiment_dict, morf, verbose)
        if verbose:
            print('Answer score:\t', score)
        final_score += score
    if verbose:
        print('Final score:\t', final_score)
    return final_score


def main():
    morf = morfeusz2.Morfeusz()
    sem_dict = load_sentiment_dict(sys.argv[1])
    with open(sys.argv[2], 'r') as file:
        thread = json.load(file)
    score = thread_sentiment_score(thread, sem_dict, morf, True)


if __name__ == "__main__":
    main()
