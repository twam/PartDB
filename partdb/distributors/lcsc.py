from .__distributor import Distributor
import re
import copy
import urllib.request
import bs4
from ..database import mergeData
import urllib.parse

import json

# https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C1525

class Lcsc(Distributor):
    def __init__(self, partDB):
        super().__init__(partDB)

    def matchBarCode(self, data):
        if isinstance(data, str):
            data = data.encode('ascii')

        data = re.sub(br'(?<=[{,])(?P<key>[a-z]*?):(?P<value>.*?)(?=[,}])', br'"\g<key>": "\g<value>"', data)
        try:
            data_dict = json.loads(data.decode('ascii'))

            result = {}
            result['distributor'] = {}
            result['distributor'][self.name()] = {}
            result['distributor'][self.name()]['distributorName'] = self.name()
            result['distributor'][self.name()]['distributorPartId'] = data_dict['pc']
            result['manufacturerPartNumber'] = data_dict['pm']
            result['quantity'] = data_dict['qty']

            return result

        except Exception as e:
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
        if 'distributorPartId' not in data['distributor'][self.name()]:
            raise Exception('No valid key found to query for data!')

        url = f"https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={data['distributor'][self.name()]['distributorPartId']}"

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

        print(jsonData)

        newData = {
            "distributor": {
                self.name(): {
                    "distributorName": self.name(),
                    "distributorPartId": data['distributor'][self.name()]['distributorPartId'],
                },
            },
        }

        if (jsonData['code'] == 200) and ('result' in jsonData):
            if 'productModel' in jsonData['result']:
                newData['manufacturerPartNumber'] = jsonData['result']['productModel']
            if 'brandNameEn' in jsonData['result']:
                newData['manufacturerName'] = jsonData['result']['brandNameEn']
            if 'productIntroEn' in jsonData['result']:
                newData['description'] = jsonData['result']['productIntroEn']
            if 'encapStandard' in jsonData['result']:
                newData['footprint'] = jsonData['result']['encapStandard']
            if 'pdfUrl' in jsonData['result']:
                newData['datasheetURL'] = jsonData['result']['pdfUrl']

        data = copy.copy(data)
        mergeData(data, newData)

        return data
