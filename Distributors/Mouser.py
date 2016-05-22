from . import __Distributor
import re
import copy
import urllib.request
import bs4
import Database
import urllib.parse
import suds.client
import logging
import config


class Mouser(__Distributor.Distributor):
    WSDL_URL = "http://www.mouser.de/service/searchapi.asmx?WSDL"

    GROUP_MAP = {
        'K': None,  # Customer PO
        '14K': None,  # Line Item
        'P': None,  # Customer P/N
        '1P': 'manufacturerPartNumber',  # Manufacturer P/N
        '1T': None,  # Batch
        'Q': 'quantity',  # Quantity
        '10D': None,  # Date Code
        'V': None,  # Supplier
        '4L': None,  # Origin
    }

    def __init__(self, partDB):
        super().__init__(partDB)

    def matchPartNumber(self, data):
        if isinstance(data, str):
            data = data.encode('ascii')

        matches = re.search(
            br'^(?P<distributorPartNumber>\d{2,3}-([-A-Z0-9./+#]+?(?<!-ND)))$', data)
        if matches:
            result = {}
            result['distributor'] = {}
            result['distributor'][self.name()] = {}
            result['distributor'][self.name()]['distributorName'] = self.name()
            result['distributor'][self.name()]['distributorPartNumber'] = matches.groupdict()[
                'distributorPartNumber'].decode('ascii')

            return result
        else:
            return None

    def matchBarCode(self, data):
        if isinstance(data, str):
            data = data.encode('ascii')

        if re.search(br'^>\[\)>(06)(\x1d[0-9]{0,2}[KPQL][-A-Z0-9,]+)+$', data):
            result = {}
            result['distributor'] = {}
            result['distributor'][self.name()] = {}
            result['distributor'][self.name()]['distributorName'] = self.name()

            pat = re.compile(
                br'(\x1d)(?P<key>[0-9]{0,2}[A-Z])(?P<value>[-A-Z0-9,]+)')
            for m in pat.finditer(data):
                key = m.groupdict()['key'].decode('ascii')
                value = m.groupdict()['value'].decode('ascii')

                if (key in self.GROUP_MAP) and (self.GROUP_MAP[key] != None):
                    result[self.GROUP_MAP[key]] = value

            return result
        else:
            return None

    def meta_redirect(self, content):
        soup = bs4.BeautifulSoup(content, 'html5lib')

        result = soup.find("meta", attrs={"http-equiv": "Refresh"})
        if result:
            wait, text = result["content"].split(";")
            if text.lower().startswith("url="):
                url = text[4:]
                return url
        return None

    def getData(self, data):
        newData = None

        if 'distributorPartNumber' not in data['distributor'][self.name()]:
            raise Exception('No valid key found to query for data!')

        distributorPartNumber = data['distributor'][
            self.name()]['distributorPartNumber']

        soapClient = suds.client.Client(self.WSDL_URL)
        mouserHeader = soapClient.factory.create('MouserHeader')
        mouserHeader.AccountInfo.PartnerID = config.MOUSER_API_KEY
        soapClient.set_options(soapheaders=mouserHeader)
        result = soapClient.service.SearchByPartNumber(distributorPartNumber)

        print(result)

        if result.NumberOfResult == 0:
            raise Exception('Part number not found.')

        partId = 0
        while True:
            if result.Parts.MouserPart[
                    0].MouserPartNumber == distributorPartNumber:
                break

            partId += 1

            if partId > result.NumberOfResult - 1:
                raise Exception('Part number not found in results.')

        print(result.Parts.MouserPart[0].Description)

        # basic data
        newData = {
            "distributor": {
                "mouser": {
                    "distributorName": "mouser",
                    "distributorPartNumber": distributorPartNumber,
                }
            },
            "manufacturerPartNumber": result.Parts.MouserPart[0].MouserPartNumber,
            "description": result.Parts.MouserPart[0].Description
        }

        # try to get some additional specs

        newData['manufacturerName'] = result.Parts.MouserPart[0].Manufacturer
        newData['datasheetURL'] = result.Parts.MouserPart[0].DataSheetUrl

        if 'Package' in result.Parts.MouserPart[0]:
            newData['footprint'] = result.Parts.MouserPart[0].Package

        data = copy.copy(data)
        Database.mergeData(data, newData)

        return data
