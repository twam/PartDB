import unittest
import unittest.mock
import Distributors.Digikey
import PartDB


class DigikeyTests(unittest.TestCase):
    DISTRIBUTORPARTNUMBERS_VALID = [
        '497-5225-1-ND',
        '296-21676-1-ND',
        '455-1163-ND',
        'S9179-ND',
        'VLMU3100-GS08CT-ND',
        'ATMEGA644P-20AU-ND',
        'TSOP34840-ND',
        'MAX214CWI+-ND']

    DISTRIBUTORPARTNUMBERS_INVALID = [
        '',
        '771-LM75BD118', # Mouser PN
        '206229100000010834647' # Digikey Barcode
    ]

    BARCODE_VALID = [
        '206229100000010834647'
    ]

    BARCODE_INVALID = [
        '497-5225-1-ND' # Digikey PN
        ''
    ]

    def setUp(self):
        self.partDB = unittest.mock.MagicMock(spec={PartDB.PartDB})
        self.digikey = Distributors.Digikey.Digikey(self.partDB)

    def testMatchPartNumberValid(self):
        for distributorPartNumber in self.DISTRIBUTORPARTNUMBERS_VALID:
            self.assertEqual(self.digikey.matchPartNumber(distributorPartNumber), {
                             'distributorPartNumber': distributorPartNumber})

    def testMatchPartNumberInvalid(self):
        for distributorPartNumber in self.DISTRIBUTORPARTNUMBERS_INVALID:
            self.assertEqual(self.digikey.matchPartNumber(
                distributorPartNumber), None)

    def testMatchBarcodeValid(self):
        for barcode in self.BARCODE_VALID:
            # only test if barcode was matched, not the actual data returned
            self.assertNotEqual(self.digikey.matchBarcode(barcode), None)

    def testMatchBarcodeInvalid(self):
        for barcode in self.BARCODE_INVALID:
            self.assertEqual(self.digikey.matchBarcode(barcode), None)
