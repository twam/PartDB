from .__distributor import Distributor
import re
import copy
import urllib.request
import bs4
from ..database import mergeData
import urllib.parse

import json

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

        url = f"https://lcsc.com/pre_search/link?type=lcsc&&value={data['distributor'][self.name()]['distributorPartId']}"

        req = urllib.request.Request(
            url, headers={'User-Agent': "electronic-parser"})
        # try:
        page = urllib.request.urlopen(req)
        # except urllib.error.HTTPError as e:
        #     if e.code == 404:
        #         return data
        #     else:
        #         raise

        soup = bs4.BeautifulSoup(page.read(), 'html5lib')

        # basic data
        infoTable = soup.find_all('table', class_='info-table')

        if (len(infoTable) == 0):
            raise Exception("Info Table not found on page")

        newData = {
            "distributor": {
                self.name(): {
                    "distributorName": self.name(),
                    "distributorPartId": data['distributor'][self.name()]['distributorPartId'],
                },
            },
        }

        for row in infoTable[0].find_all('tr'):
            cells = row.find_all(re.compile("^t[hd]$"))
            if (len(cells) >= 2):
                key = cells[0].get_text().strip()
                val = cells[1].get_text().strip()

                if key == 'Mfr.Part #':
                    newData['manufacturerPartNumber'] = val
                if key == 'Manufacturer':
                    newData['manufacturerName'] = val
                if key == 'Description':
                    newData['description'] = val
                elif key == 'Package':
                    newData['footprint'] = val
                elif key == 'Datasheet':
                    val = cells[1].find_all('a')[0]['href']
                    newData['datasheetURL'] = val

        data = copy.copy(data)
        mergeData(data, newData)

        return data
