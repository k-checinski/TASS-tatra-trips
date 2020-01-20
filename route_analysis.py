from typing import Set, List
import morfeusz2
from pl_stemmer import stem


def is_sufficient(prepared_tuple):
    part_of_speech = prepared_tuple[1].split(':')[0]
    return part_of_speech in ['adj', 'ign']


def prepare_objects(terms):
    morf = morfeusz2.Morfeusz()
    prepared_objects = []
    for term in terms:
        words = term['name'].split(' ')
        words_results = [morf.analyse(w) for w in words]
        prepared_words = []
        for word_result in words_results:
            info = process_word(word_result)
            prepared_result = [(w[1], w[2].split(':')[0]) for w in info]
            forms = set([r[0].split(':')[0].lower() for r in prepared_result])
            prepared_words.append((forms, any([is_sufficient(t) for t in prepared_result])))
        prepared_objects.append({'keywords': prepared_words, 'type': term['type'],
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
        if morf_tuple[0] != pos:
            if len(current_set) != 0:
                sets.append(current_set)
                current_set = set()
            pos = morf_tuple[0]
        lemma = morf_tuple[2][1].split(':')[0]
        part_of_speech = morf_tuple[2][2].split(':')[0]
        if part_of_speech == 'ign':
            lemma = stem(lemma)
        lemma = ''.join(c for c in lemma if c.isalnum())
        if len(lemma) > 0:
            current_set.add(lemma)
    return sets


def find_next_object(text_lemmas_sets, start_pos, objects_dict):
    matches = []
    min_length = 0
    for object in objects_dict:
        current_pos = start_pos
        all_matched = True
        sufficient_matched = False
        for keyword in object['keywords']:
            overlap = not keyword[0].isdisjoint(text_lemmas_sets[current_pos])
            if overlap and keyword[1]:
                sufficient_matched = True
                break
            if not overlap:
                all_matched = False
            current_pos += 1
            if current_pos >= len(text_lemmas_sets):
                all_matched = False
                break
        if all_matched or sufficient_matched:
            matches.append(object)
            if len(object['keywords']) < min_length or min_length == 0:
                min_length = len(object['keywords'])
    return matches, start_pos + min_length


if __name__ == '__main__':
    import json
    with open('resources/geo.json', 'r') as file:
        objs = json.load(file)
    prep = prepare_objects(objs)
    with open('threads/0_5007.json') as file:
        thread = json.load(file)
    text = thread['answers'][0]['content']
    print(text)
    sets = prepare_text(text, morfeusz2.Morfeusz())
    print(sets[58:70])
    result = find_next_object(sets[58:70], 0, prep)
    for obj in result[0]:
        print(obj)

# TODO obliczanie długości dopasowania i zwracanie jej w krotce wyniku
