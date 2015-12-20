import unittest
import Database
import os
import time
import uuid


class DatabaseTests(unittest.TestCase):
    TESTDATABASEFILENAME = '/tmp/test.json'

    TESTENTRY1 = {
        "manufacturerPartNumber": "A1",
        "description": "Test Part 1",
        "quantity": 1
    }

    TESTENTRY2 = {
        "manufacturerPartNumber": "B2",
        "description": "Test Part 2",
        "quantity": 2
    }

    TESTENTRY3 = {
        "manufacturerPartNumber": "C3",
        "description": "Test Part 3",
        "quantity": 3
    }

    def assertAEqualInBEntry(self, a, b):
        ''' Checks if all elements of a are the same in b (not vice versa!) '''
        for key, val in a.items():
            self.assertEqual(val, b[key])

    def setUp(self):
        if os.path.isfile(self.TESTDATABASEFILENAME):
            os.remove(self.TESTDATABASEFILENAME)

        self.db = Database.Database(self.TESTDATABASEFILENAME)

    def tearDown(self):
        # close database so file will actually be written
        del self.db

        if os.path.isfile(self.TESTDATABASEFILENAME):
            # delete test database again
            os.remove(self.TESTDATABASEFILENAME)
        else:
            raise Exception('Test database %s was not written!' %
                            (self.TESTDATABASEFILENAME))

    def testAssureTypesEmpty(self):
        data = {}
        self.db.assureTypes(data)
        self.assertEqual({}, data)

    def testAssureTypesCorrectTypes(self):
        data = {'quantity': 5}
        self.db.assureTypes(data)
        self.assertEqual({'quantity': 5}, data)

    def testAssureTypesIncorrectTypes(self):
        data = {'quantity': '5'}
        self.db.assureTypes(data)
        self.assertEqual({'quantity': 5}, data)

    def testAssureTypesCorrectTypesWithDistributor(self):
        data = {
            'quantity': 5,
            'distributor': {
                'digikey': {
                    'distributorPartNumber': '5'
                }
            }
        }
        self.db.assureTypes(data)
        self.assertEqual({
            'quantity': 5,
            'distributor': {
                'digikey': {
                    'distributorPartNumber': '5'
                }
            }
        }, data)

    def testAssureTypesIncorrectTypesWithDistributor(self):
        data = {
            'quantity': 5,
            'distributor': {
                'digikey': {
                    'distributorPartNumber': 5
                }
            }
        }
        self.db.assureTypes(data)
        self.assertEqual({
            'quantity': 5,
            'distributor': {
                'digikey': {
                    'distributorPartNumber': '5'
                }
            }
        }, data)

    def testAdd(self):
        self.db.add(self.TESTENTRY1)

        partKey = list(self.db.raw().keys())[0]
        partData = self.db.raw()[partKey]

        # Check timestampCreated is quite recent
        self.assertTrue(partData['timestampCreated'] - time.time() < 1)

        # Check timestampCreated and timestampLastModified are the same
        self.assertEqual(partData['timestampCreated'],
                         partData['timestampLastModified'])

        # Check all data elements are correct
        self.assertAEqualInBEntry(self.TESTENTRY1, partData)

    def testDelete(self):
        # add a test entry
        self.db.add(self.TESTENTRY1)

        # get key of test entry
        partKey = list(self.db.raw().keys())[0]

        # delete entry again
        self.db.delete(partKey)

        # check if db is empty again
        self.assertEqual(self.db.raw(), {})

    def testDeleteFail(self):
        with self.assertRaises(Exception):
            # delete a random entry
            self.db.delete(str(uuid.uuid4()))

    def testQueryDataEntry(self):
        self.db.add(self.TESTENTRY1)

        result = self.db.query(addDefaults=False)

        # get key of test entry
        partKey = list(result.keys())[0]
        partData = result[partKey]

        # Check all data elements are correct
        self.assertAEqualInBEntry(self.TESTENTRY1, partData)

        # Make sure defaults have NOT been added
        self.assertTrue('manufacturerName' not in partData)

    def testQueryWithAddDefault(self):
        self.db.add(self.TESTENTRY1)

        result = self.db.query(addDefaults=True)

        # get key of test entry
        partKey = list(result.keys())[0]
        partData = result[partKey]

        # Check all data elements are correct
        self.assertEqual(partData['manufacturerName'], '')

    def testQueryNoResult(self):
        self.db.add(self.TESTENTRY1)
        self.db.add(self.TESTENTRY2)
        self.db.add(self.TESTENTRY3)

        result = self.db.query(filter=lambda k, v: False)

        self.assertEqual(result, {})

    def testQuerySingleResult(self):
        self.db.add(self.TESTENTRY1)
        self.db.add(self.TESTENTRY2)
        self.db.add(self.TESTENTRY3)

        result = self.db.query(filter=lambda k, v: v[
                               'manufacturerPartNumber'] == 'B2')

        # get key of test entry
        partKey = list(result.keys())[0]
        partData = result[partKey]

        self.assertAEqualInBEntry(self.TESTENTRY2, partData)

    def testQueryOrderBy(self):
        self.db.add(self.TESTENTRY3)
        self.db.add(self.TESTENTRY1)
        self.db.add(self.TESTENTRY2)

        result = self.db.query()

        self.assertEqual(result[list(result.keys())[0]][
                         'manufacturerPartNumber'], 'A1')
        self.assertEqual(result[list(result.keys())[1]][
                         'manufacturerPartNumber'], 'B2')
        self.assertEqual(result[list(result.keys())[2]][
                         'manufacturerPartNumber'], 'C3')

    def testUpdate(self):
        data = self.db.add(self.TESTENTRY1)

        # change data
        data['manufacturerPartNumber'] = 'A1+'
        self.db.update(data)

        # remove last timestampLastModified as this will differ
        del data['timestampLastModified']

        self.assertAEqualInBEntry(data, self.db.raw()[data['id']])

    def testUpdateFail(self):
        with self.assertRaises(Exception):
            self.db.update(str(uuid.uuid4()), self.TESTENTRY1)

    def testContainsTrue(self):
        self.db.add(self.TESTENTRY1)

        # get key of test entry
        partKey = list(self.db.raw().keys())[0]

        self.assertTrue(partKey in self.db)

    def testContainsFails(self):
        self.assertTrue(str(uuid.uuid4()))

    def testMergeDataBothEmpty(self):
        dest = {}
        src = {}

        Database.mergeData(dest, src)

        self.assertEqual(dest, {})

    def testMergeDataDataOnlyInSrc(self):
        dest = {}
        src = {'a': 'A'}

        Database.mergeData(dest, src)

        self.assertEqual(dest, {'a': 'A'})

    def testMergeDataDataOnlyInDest(self):
        dest = {'a': 'A'}
        src = {}

        Database.mergeData(dest, src)

        self.assertEqual(dest, {'a': 'A'})

    def testMergeDataDataInBothNoOverride(self):
        dest = {'a': 'DEST'}
        src = {'a': 'SRC'}

        Database.mergeData(dest, src, override=False)

        self.assertEqual(dest, {'a': 'DEST'})

    def testMergeDataDataInBothOverride(self):
        dest = {'a': 'DEST'}
        src = {'a': 'SRC'}

        Database.mergeData(dest, src, override=True)

        self.assertEqual(dest, {'a': 'SRC'})

    def testMergeDataDictOnlyInSrc(self):
        dest = {}
        src = {'a': {'a1': 'A1'}}

        Database.mergeData(dest, src)

        self.assertEqual(dest, {'a': {'a1': 'A1'}})

    def testMergeDataDictDataBothNoOverride(self):
        dest = {'a': {'a1': 'DEST'}}
        src = {'a': {'a1': 'SRC'}}

        Database.mergeData(dest, src, override=False)

        self.assertEqual(dest, {'a': {'a1': 'DEST'}})

    def testMergeDataDictDataBothOverride(self):
        dest = {'a': {'a1': 'DEST'}}
        src = {'a': {'a1': 'SRC'}}

        Database.mergeData(dest, src, override=True)

        self.assertEqual(dest, {'a': {'a1': 'SRC'}})
