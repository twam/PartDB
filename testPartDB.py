import unittest
import unittest.mock
import collections
import os
import Database
import PartDB


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

    TESTENTRIES = collections.OrderedDict(sorted({
        '11111111-1111-1111-1111-111111111111': TESTENTRY1,
        '22222222-2222-2222-2222-222222222222': TESTENTRY2,
        '33333333-3333-3333-3333-333333333333': TESTENTRY3,
    }.items(), key=lambda t: t[0]))

    def setUp(self):
        patchDatabase = unittest.mock.patch("Database.Database", autospec=True)
        self.mockDatabase = patchDatabase.start()
        self.addCleanup(patchDatabase.stop)

        patchPrint = unittest.mock.patch("builtins.print", autospec=True)
        self.mockPrint = patchPrint.start()
        self.addCleanup(patchPrint.stop)

    def tearDown(self):
        pass

    def testDisplayListWithoutKeys(self):
        partDB = PartDB.PartDB('PartDB'.split(' '))

        partDB.displayList(self.TESTENTRIES, showKeys=False)

        expected_output = '''
            Part Number          | Description                                        | Quantity  
            ---------------------|----------------------------------------------------|-----------
            A1                   | Test Part 1                                        | 1         
            B2                   | Test Part 2                                        | 2         
            C3                   | Test Part 3                                        | 3         
            ---------------------|----------------------------------------------------|-----------'''.split("\n            ")

        line = 1
        for call in self.mockPrint.call_args_list:
            self.assertTrue(line < len(expected_output))
            self.assertEqual(call, call(expected_output[line]))
            line += 1

    def testDisplayListWithKeys(self):
        partDB = PartDB.PartDB('PartDB'.split(' '))

        partDB.displayList(self.TESTENTRIES, showKeys=True)

        expected_output = '''
            ID                                   | Part Number          | Description                                        | Quantity  
            -------------------------------------|----------------------|----------------------------------------------------|-----------
            11111111-1111-1111-1111-111111111111 | A1                   | Test Part 1                                        | 1         
            22222222-2222-2222-2222-222222222222 | B2                   | Test Part 2                                        | 2         
            33333333-3333-3333-3333-333333333333 | C3                   | Test Part 3                                        | 3         
            -------------------------------------|----------------------|----------------------------------------------------|-----------'''.split("\n            ")

        line = 1
        for call in self.mockPrint.call_args_list:
            self.assertTrue(line < len(expected_output))
            self.assertEqual(call, call(expected_output[line]))
            line += 1

    def testDatabaseArgument(self):
        with unittest.mock.patch("Commands.List.List", autospec=True) as mockCommandList:
            partDB = PartDB.PartDB(
                'PartDB -d /somedirectory/anotherdatabase.json list'.split(' '))
            partDB.run()

        self.mockDatabase.assert_called_once_with(
            '/somedirectory/anotherdatabase.json')
