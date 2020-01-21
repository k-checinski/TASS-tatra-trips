import constants


class GeoItem:
    def __init__(self, name, object_type, latitude='0°0', longitude='0°0'):
        self.name = name
        self.type = object_type
        self.latitude = self.parse_coordination_string(latitude)
        self.longitude = self.parse_coordination_string(longitude)

    @staticmethod
    def parse_coordination_string(coord):
        coord_string = coord.split('\'')[0]
        degrees = int(coord_string.split('°')[0])
        minutes = int(coord_string.split('°')[1])
        seconds = int(coord.split('\'')[1]) if len(coord.split('\'')) > 1 else 0
        return degrees + minutes / 60 + seconds / 3600

    def is_located_in_tatra_region(self):
        return constants.MIN_LATITUDE < self.latitude < constants.MAX_LATITUDE \
               and constants.MIN_LONGITUDE < self.longitude < constants.MAX_LONGITUDE
