import csv
import json

class SentimentItem:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


class MyEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def main():
    dictionary = []
    with open('resources/sentyment.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue

            name = row["słowo"]
            weight = row["waga"]
            dictionary.append(SentimentItem(name, weight))


    with open('resources/sentiment.json', 'w') as outfile:
        json.dump(dictionary, outfile, cls=MyEncoder, ensure_ascii=False)

if __name__ == '__main__':
    main()
