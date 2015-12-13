import PersistentDict
import collections
import copy
import uuid
import time


class Database:
    KEYS = {
        'manufacturerPartNumber': {'type': str, 'default': ''},
        'manufacturerName': {'type': str, 'default': ''},
        'description': {'type': str, 'default': ''},
        'quantity': {'type': int, 'default': 0},
        'distributor': {'type': dict, 'default': {}},
        'datasheetURL': {'type': str, 'default': ''},
        'timestampCreated': {'type': float, 'default': 0.0},
        'timestampLastModified': {'type': float, 'default': 0.0},
    }

    def __init__(self, filename):
        self.filename = filename
        self.persistentDict = PersistentDict.PersistentDict(
            self.filename, format='json')

    def __del__(self):
        self.persistentDict.close()

    def addDefaults(self, d):
        for key, value in self.KEYS.items():
            d.setdefault(key, value['default'])

        return d

    def raw(self):
        return self.persistentDict

    def query(self, orderBy='manufacturerPartNumber', filter=None, addDefaults=True):
        filteredDict = {k: self.addDefaults(copy.copy(v)) if addDefaults else copy.copy(
            v) for k, v in self.persistentDict.items() if (filter(k) if filter != None else True)}
        return collections.OrderedDict(sorted(filteredDict.items(), key=lambda t: t[1][orderBy]))

    def add(self, val):
        # create key for part and make sure that is not already preset
        partKey = None
        while (partKey == None) or (partKey in self.persistentDict):
            partKey = str(uuid.uuid4())

        partData = copy.copy(val)

        # add timestamps
        partData['timestampCreated'] = time.time()
        partData['timestampLastModified'] = time.time()

        self.persistentDict[partKey] = partData

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
