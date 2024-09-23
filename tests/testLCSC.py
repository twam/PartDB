import unittest
import unittest.mock
from partdb.distributors.lcsc import Lcsc
from partdb.__main__ import PartDB


class LCSCTests(unittest.TestCase):
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
        b'{pbn:PICK2101290004,on:SO2101287934,pc:C24966,pm:TPS63000DRCR,qty:10,mc:,cc:1,pdi:39241148}',
    ]

    BARCODE_INVALID = [
        b'{abc:Hello}',
        '206229100000010834647'  # Digikey barcode
        ''
    ]

    def setUp(self):
        self.partDB = unittest.mock.MagicMock(spec={PartDB})
        self.lcsc = Lcsc(self.partDB)

    # def testMatchPartNumberValid(self):
    #     for distributorPartNumber in self.DISTRIBUTORPARTNUMBERS_VALID:
    #         # only test if part number was matched, not the actual data
    #         # returned
    #         self.assertNotEqual(self.lcsc.matchPartNumber(
    #             distributorPartNumber), None)

    def testMatchPartNumberInvalid(self):
        for distributorPartNumber in self.DISTRIBUTORPARTNUMBERS_INVALID:
            self.assertEqual(self.lcsc.matchPartNumber(
                distributorPartNumber), None)

    def testMatchBarCodeValid(self):
        for barcode in self.BARCODE_VALID:
            # only test if barcode was matched, not the actual data returned
            self.assertNotEqual(self.lcsc.matchBarCode(barcode), None)

    def testMatchBarCodeInvalid(self):
        for barcode in self.BARCODE_INVALID:
            self.assertEqual(self.lcsc.matchBarCode(barcode), None)
