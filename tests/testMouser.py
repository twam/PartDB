import unittest
import unittest.mock
from partdb.distributors.mouser import Mouser
from partdb.__main__ import PartDB


class MouserTests(unittest.TestCase):
    DISTRIBUTORPARTNUMBERS_VALID = [
        '771-LM75BD118',
        '739-BMIS-202-F',
        '963-JMK325ABJ227MM-T',
        '960-IAA.01.121111',
        '71-CRCW0603-86.6K-E3',
        '70-IHLP4040DZERR56M0',
        '579-MCP3428E/SL',
        '700-DS3232MZ+',
        '523-12401548E4#2A',
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
        '2302279',  # Farnell PN
    ]

    BARCODE_VALID = [
        # Mouser barcode with mfg p/n
        b'>[)>06\x1dK9585766\x1d14K005\x1d1PLM75BD,118\x1dQ10\x1d11K039518665\x1d4LTH',
        b'>[)>06\x1dK9585766\x1d14K004\x1d1PJMK325ABJ227MM-T\x1dQ2\x1d11K039518665\x1d4LJP',
        # Mouser barcode with cust p/n
        b'>[)>06\x1dK8501032\x1d14K019\x1dPBTTF\x1dQ5\x1d11K037426481\x1d4LIL',
    ]

    BARCODE_INVALID = [
        '206229100000010834647'  # Digikey barcode
        ''
    ]

    def setUp(self):
        self.partDB = unittest.mock.MagicMock(spec={PartDB})
        self.mouser = Mouser(self.partDB)

    def testMatchPartNumberValid(self):
        for distributorPartNumber in self.DISTRIBUTORPARTNUMBERS_VALID:
            # only test if part number was matched, not the actual data
            # returned
            self.assertNotEqual(self.mouser.matchPartNumber(
                distributorPartNumber), None)

    def testMatchPartNumberInvalid(self):
        for distributorPartNumber in self.DISTRIBUTORPARTNUMBERS_INVALID:
            self.assertEqual(self.mouser.matchPartNumber(
                distributorPartNumber), None)

    def testMatchBarCodeValid(self):
        for barcode in self.BARCODE_VALID:
            # only test if barcode was matched, not the actual data returned
            self.assertNotEqual(self.mouser.matchBarCode(barcode), None)

    def testMatchBarCodeInvalid(self):
        for barcode in self.BARCODE_INVALID:
            self.assertEqual(self.mouser.matchBarCode(barcode), None)
