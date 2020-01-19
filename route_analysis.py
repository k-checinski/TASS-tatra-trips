import morfeusz2
from sentiment_analysis import lemmas_list
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
            info = [list(w[2]) for w in word_result]
            for result_tuple in info:
                if result_tuple[2] == 'ign':
                    result_tuple[1] = stem(result_tuple[1])
            prepared_result = [(w[1], w[2].split(':')[0]) for w in info]
            forms = set([r[0].split(':')[0].lower() for r in prepared_result])
            prepared_words.append((forms, any([is_sufficient(t) for t in prepared_result])))
        prepared_objects.append({'keywords': prepared_words, 'type': term['type'],
                                'latitude': term['latitude'], 'longitude': term['longitude']})

    return prepared_objects





