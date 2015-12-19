import unittest
import unittest.mock
import Distributors.Farnell
import PartDB


class FarnellTests(unittest.TestCase):
    DISTRIBUTORPARTNUMBERS_VALID = [
        '2302279',
    ]

    DISTRIBUTORPARTNUMBERS_INVALID = [
        '',
        '497-5225-1-ND',  # Digikey PN
        '296-21676-1-ND',  # Digikey PN
        '455-1163-ND',  # Digikey PN
        'S9179-ND',  # Digikey PN
        'VLMU3100-GS08CT-ND',  # Digikey PN
        'ATMEGA644P-20AU-ND',  # Digikey PN
        'TSOP34840-ND',  # Digikey PN
        'MAX214CWI+-ND',  # Digikey PN
        '206229100000010834647',  # Digikey Barcode
        '771-LM75BD118',  # Mouser PN
        '739-BMIS-202-F',  # Mouser PN
        '963-JMK325ABJ227MM-T',  # Mouser PN
        '960-IAA.01.121111',  # Mouser PN
        '71-CRCW0603-86.6K-E3',  # Mouser PN
        '70-IHLP4040DZERR56M0',  # Mouser PN
    ]

    BARCODE_VALID = [
    ]

    BARCODE_INVALID = [
        '206229100000010834647'  # Digikey barcode
        ''
    ]

    def setUp(self):
        self.partDB = unittest.mock.MagicMock(spec={PartDB.PartDB})
        self.farnell = Distributors.Farnell.Farnell(self.partDB)

    def testMatchPartNumberValid(self):
        for distributorPartNumber in self.DISTRIBUTORPARTNUMBERS_VALID:
            # only test if part number was matched, not the actual data
            # returned
            self.assertNotEqual(self.farnell.matchPartNumber(
                distributorPartNumber), None)

    def testMatchPartNumberInvalid(self):
        for distributorPartNumber in self.DISTRIBUTORPARTNUMBERS_INVALID:
            self.assertEqual(self.farnell.matchPartNumber(
                distributorPartNumber), None)

    def testMatchBarCodeValid(self):
        for barcode in self.BARCODE_VALID:
            # only test if barcode was matched, not the actual data returned
            self.assertNotEqual(self.farnell.matchBarCode(barcode), None)

    def testMatchBarCodeInvalid(self):
        for barcode in self.BARCODE_INVALID:
            self.assertEqual(self.farnell.matchBarCode(barcode), None)
