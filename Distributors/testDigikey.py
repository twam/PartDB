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
        '2302279',  # Farnell PN
        '206229100000010834647'  # Digikey Barcode
        '771-LM75BD118',  # Mouser PN
        '739-BMIS-202-F',  # Mouser PN
        '963-JMK325ABJ227MM-T',  # Mouser PN
        '960-IAA.01.121111',  # Mouser PN
        '71-CRCW0603-86.6K-E3',  # Mouser PN
        '70-IHLP4040DZERR56M0'  # Mouser PN
    ]

    BARCODE_VALID = [
        '2062291000000010834647',
        '2077771000000005327423',
        '1786439000000040970571',
        '3592994000000003521262',
    ]

    BARCODE_INVALID = [
        '497-5225-1-ND',  # Digikey PN
        b'>[)>06\x1dK9585766\x1d14K005\x1d1PLM75BD,118\x1dQ10\x1d11K039518665\x1d4LTH', # Mouser barcode with mfg p/n
        b'>[)>06\x1dK9585766\x1d14K004\x1d1PJMK325ABJ227MM-T\x1dQ2\x1d11K039518665\x1d4LJP', 
        b'>[)>06\x1dK8501032\x1d14K019\x1dPBTTF\x1dQ5\x1d11K037426481\x1d4LIL', # Mouser barcode with cust p/n
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

    def testMatchBarCodeValid(self):
        for barcode in self.BARCODE_VALID:
            # only test if barcode was matched, not the actual data returned
            self.assertNotEqual(self.digikey.matchBarCode(barcode), None)

    def testMatchBarCodeInvalid(self):
        for barcode in self.BARCODE_INVALID:
            self.assertEqual(self.digikey.matchBarCode(barcode), None)
