import PersistentDict
import collections
import copy
import uuid
import time


def mergeData(dest, src, override=False):
    '''Merges all data from src into dst. If override is True already available data is overridden'''
    for key, val in src.items():
        if ((key in dest) and (type(dest[key]) != dict) and (override == True)) or (key not in dest):
            dest[key] = val
        elif (key in dest) and (type(dest[key]) == dict):
            mergeData(dest[key], val, override=override)


class Database:
    KEYS = {
        'manufacturerPartNumber': {'type': str, 'default': '', 'help': 'Part number specified by the manufacturer.', 'argument': '-p'},
        'manufacturerName': {'type': str, 'default': '', 'help': 'Name of the manufacturer.', 'argument': None},
        'description': {'type': str, 'default': '', 'help': 'Description of the part.', 'argument': '-d'},
        'quantity': {'type': int, 'default': 0, 'help': 'Quantity available.', 'argument': '-q'},
        'distributor': {'type': dict, 'default': {}, 'help': 'Distributor information.'},
        'datasheetURL': {'type': str, 'default': '', 'help': 'URL to datasheet.', 'argument': None},
        'timestampCreated': {'type': float, 'default': 0.0, 'help': 'Time of entry creation.'},
        'timestampLastModified': {'type': float, 'default': 0.0, 'help': 'Time of last update.'},
    }

    KEYS_DISTRIBUTOR = {
        'distributorPartNumber': {'type': str, 'default': '', 'help': 'Part number specified by the distributor.', 'argument': None},
        'distributorName': {'type': str, 'default': '', 'help': 'Name of the distributor.', 'argument': None}
    }

    def __init__(self, filename):
        self.filename = filename
        self.persistentDict = PersistentDict.PersistentDict(
            self.filename, format='json')

    def __del__(self):
        self.persistentDict.close()

    def __contains__(self, key):
        return key in self.persistentDict

    def addDefaults(self, d):
        for key, value in self.KEYS.items():
            d.setdefault(key, value['default'])

        return d

    def raw(self):
        return self.persistentDict

    def query(self, orderBy='manufacturerPartNumber', filter=None, addDefaults=True):
        filteredDict = {k: self.addDefaults(copy.copy(v)) if addDefaults else copy.copy(
            v) for k, v in self.persistentDict.items() if (filter(k, v) if filter != None else True)}
        return collections.OrderedDict(sorted(filteredDict.items(), key=lambda t: t[1][orderBy]))

    def add(self, val):
        # create key for part and make sure that is not already preset
        partKey = None
        while (partKey == None) or (partKey in self.persistentDict):
            partKey = str(uuid.uuid4())

        partData = copy.copy(val)

        # add timestamps
        partData['timestampCreated'] = time.time()
        partData['timestampLastModified'] = partData['timestampCreated']

        self.persistentDict[partKey] = partData

        return partKey

    def update(self, partKey, val):
        # check if key is existent
        if partKey not in self.persistentDict:
            raise Exception('Key \'%s\' not in database.' % (partKey))

        partData = copy.copy(val)

        # update timestamps
        partData['timestampLastModified'] = time.time()

        self.persistentDict[partKey] = partData

    def delete(self, partKey):
        # check if key is existent
        if partKey not in self.persistentDict:
            raise Exception('Key \'%s\' not in database.' % (partKey))

        del self.persistentDict[partKey]
