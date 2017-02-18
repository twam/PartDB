from . import __Distributor
import re
import copy
import json
import urllib
import Database
import config

class Farnell(__Distributor.Distributor):

    def __init__(self, partDB):
        super().__init__(partDB)

    def matchPartNumber(self, data):
        if isinstance(data, str):
            data = data.encode('ascii')

        matches = re.search(
            br'^(?P<distributorPartNumber>\d{7})$', data)
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
        return None

    def getData(self, data):
        newData = {}

        if 'distributorPartNumber' in data['distributor'][self.name()]:
            url = "http://api.element14.com//catalog/products?term=id:{}&storeInfo.id=uk.farnell.com&resultsSettings.offset=0&resultsSettings.numberOfResults=1&resultsSettings.refinements.filters=&resultsSettings.responseGroup=large&callInfo.omitXmlSchema=false&callInfo.callback=&callInfo.responseDataFormat=json&callinfo.apiKey={}".format(
                data['distributor'][self.name()]['distributorPartNumber'],
                config.FARNELL_API_KEY
            )
        else:
            raise Exception('No valid key found to query for data!')

        req = urllib.request.Request(
            url, headers={'User-Agent': "electronic-parser"})
        # try:
        page = urllib.request.urlopen(req)
        # except urllib.error.HTTPError as e:
        #     if e.code == 404:
        #         return data
        #     else:
        #         raise
        rawData = page.read().decode('utf_8')
        jsonData = json.loads(rawData)

        if (jsonData['premierFarnellPartNumberReturn']
                ['numberOfResults'] == 0):
            raise Exception('Product not found')

        productData = jsonData['premierFarnellPartNumberReturn']['products'][0]

        newData = {
            "distributor": {
                "farnell": {
                    "distributorName": "farnell",
                    "distributorPartNumber": productData['sku'],
                },
            },
            "manufacturerPartNumber": productData['translatedManufacturerPartNumber'],
            "manufacturerName": productData['vendorName'],
            "description": productData['displayName']
        }

        if 'attributes' in productData:
            for attribute in productData['attributes']:
                if attribute['attributeLabel'].strip(
                ) == 'Alternate Case Style':
                    newData['footprint'] = attribute['attributeValue']
                    if 'attributeUnit' in attribute:
                        newData['footprint'] += attribute['attributeUnit']

        if 'datasheets' in productData:
            for datasheet in productData['datasheets']:
                if datasheet['description'] == 'Technical Data Sheet':
                    if 'datasheetURL' in newData:
                        raise('Datasheet already there!')
                    newData['datasheetURL'] = datasheet['url']

        data = copy.copy(data)
        Database.mergeData(data, newData)

        return data
