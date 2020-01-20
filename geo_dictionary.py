import csv
import json

import overpy
import constants

from GeoItem import GeoItem


class MyEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

def main():
    geo_items = []
    distinct_names = []
    with open('resources/obiekty_fizjograficzne.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue

            object_name = row["nazwa główna"]

            if object_name in distinct_names or object_name in constants.REJECTED_OBJECTS:
                continue

            object_type = row["rodzaj obiektu"]
            if not set(object_type.split(':')).isdisjoint(constants.REJECTED_OBJECT_TYPES):
                continue

            object_latitude = row["szerokość geograficzna"]
            object_longitude = row["długość geograficzna"]
            geo_object = GeoItem(object_name, object_type, object_latitude, object_longitude)

            if geo_object.is_located_in_tatra_region():
                geo_items.append(geo_object)
                distinct_names.append(object_name)

    api = overpy.Overpass()
    results = api.query("""way["tourism"="alpine_hut"](49,19.1,49.34,20.2);out;""")
    for result in results.ways:
        if result.tags.get("addr:country") == constants.SLOVAKIA_CODE:
            continue
        name = result.tags.get("name")
        geo_items.append(GeoItem(name, constants.TOURIST_SHELTER))

    with open('resources/geo.json', 'w') as outfile:
        json.dump(geo_items, outfile, cls=MyEncoder, ensure_ascii=False)


if __name__ == '__main__':
    main()
