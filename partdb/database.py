import collections
import copy
import uuid
import time

from .persistent_dict import PersistentDict



def mergeData(dest, src, override=False):
    '''Merges all data from src into dst. If override is True already
        available data is overridden'''
    for key, val in src.items():
        if ((key in dest) and (not isinstance(dest[key], dict)) and (
                override == True)) or (key not in dest):
            dest[key] = val
        elif (key in dest) and (isinstance(dest[key], dict)):
            mergeData(dest[key], val, override=override)


class Database:
    SCHEMA = {
        'manufacturerPartNumber': {
            'type': str,
            'default': '',
            'help': 'Part number specified by the manufacturer.',
            'argument': '-p'},
        'manufacturerName': {
            'type': str,
            'default': '',
            'help': 'Name of the manufacturer.',
            'argument': None},
        'description': {
            'type': str,
            'default': '',
            'help': 'Description of the part.',
            'argument': '-d'},
        'quantity': {
            'type': int,
            'default': 0,
            'help': 'Quantity available.',
            'argument': '-q'},
        'footprint': {
            'type': str,
            'default': '',
            'help': 'footprint of part',
            'argument': None},
        'manufacturerFootprint': {
            'type': str,
            'default': '',
            'help': 'manufacturer specific name of footprint',
            'argument': None},
        'distributor': {
            'type': dict,
            'default': {},
            'help': 'Distributor information.',
            'entries': {
                'distributorPartId': {
                    'type': str,
                    'default': '',
                    'help': 'Part ID specified by the distributor.',
                    'argument': None},
                'distributorPartNumber': {
                    'type': str,
                    'default': '',
                    'help': 'Part number specified by the distributor.',
                    'argument': None},
                'distributorName': {
                    'type': str,
                    'default': '',
                    'help': 'Name of the distributor.',
                    'argument': None},
            }
        },
        'datasheetURL': {
            'type': str,
            'default': '',
            'help': 'URL to datasheet.',
            'argument': None},
        'timestampCreated': {
            'type': float,
            'default': 0.0,
            'help': 'Time of entry creation.',
            'formatter': lambda x: time.strftime('%d.%m.%Y %H:%M', time.gmtime(x))},
        'timestampLastModified': {
            'type': float,
            'default': 0.0,
            'help': 'Time of last update.',
            'formatter': lambda x: time.strftime('%d.%m.%Y %H:%M', time.gmtime(x))},
    }

    KEYS_DISTRIBUTOR = SCHEMA['distributor']['entries']

    def __init__(self, filename: str):
        self.filename = filename
        self.persistentDict = PersistentDict(
            self.filename, format='json')

    def __del__(self):
        self.persistentDict.close()

    def __contains__(self, key):
        return key in self.persistentDict

    def addDefaults(self, data):
        for key, value in self.SCHEMA.items():
            data.setdefault(key, value['default'])

        return data

    def assureTypes(self, data, schema=SCHEMA):
        for key in data:
            if ((key in schema) and
                    (not isinstance(data[key], schema[key]['type']))):
                data[key] = schema[key]['type'](data[key])

            if 'entries' in schema[key]:
                for key2 in data[key]:
                    self.assureTypes(data[key][key2], schema[key]['entries'])

    def raw(self):
        return self.persistentDict

    def query(self, orderBy='manufacturerPartNumber',
              filter=None, addDefaults=True):
        filteredDict = {k: self.addDefaults(copy.copy(v)) if addDefaults else copy.copy(
            v) for k, v in self.persistentDict.items() if (filter(k, v) if filter is not None else True)}
        return collections.OrderedDict(
            sorted(filteredDict.items(), key=lambda t: t[1][orderBy]))

    def add(self, val):
        # create key for part and make sure that is not already preset
        id_ = None
        while (id_ is None) or (id_ in self.persistentDict):
            id_ = str(uuid.uuid4())

        partData = copy.copy(val)

        # add timestamps
        partData['timestampCreated'] = time.time()
        partData['timestampLastModified'] = partData['timestampCreated']
        partData['id'] = id_

        self.persistentDict[id_] = partData

        return partData

    def update(self, data):
        # check if key is existent
        if data['id'] not in self.persistentDict:
            raise Exception('ID \'%s\' not in database.' % (data['id']))

        partData = copy.copy(data)

        # update timestamps
        partData['timestampLastModified'] = time.time()

        self.persistentDict[data['id']] = partData

    def delete(self, id_):
        # check if key is existent
        if id_ not in self.persistentDict:
            raise Exception('ID \'%s\' not in database.' % (id_))

        del self.persistentDict[id_]
