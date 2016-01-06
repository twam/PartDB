from . import __Distributor
import re
import copy
import bs4
import urllib
import Database


class Digikey(__Distributor.Distributor):

    def __init__(self, partDB):
        super().__init__(partDB)

    def matchPartNumber(self, data):
        if isinstance(data, str):
            data = data.encode('ascii')

        matches = re.search(
            br'^(?P<distributorPartNumber>[-+A-Z0-9#/]+-ND)$', data)
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

        matches = re.search(
            br'^(?P<distributorPartId>\d{7})(?P<quantity>\d{9})(\d{6})$', data)
        if matches:
            result = {}
            result['distributor'] = {}
            result['distributor'][self.name()] = {}
            result['distributor'][self.name()]['distributorName'] = self.name()
            result['distributor'][self.name()]['distributorPartId'] = matches.groupdict()[
                'distributorPartId'].decode('ascii')
            result['quantity'] = matches.groupdict()['quantity']

            return result
        else:
            return None

    def getData(self, data):
        newData = None

        if 'distributorPartNumber' in data['distributor'][self.name()]:
            url = "http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail&name={}".format(
                urllib.parse.quote(data['distributor'][self.name()]['distributorPartNumber']))
        elif 'distributorPartId' in data['distributor'][self.name()]:
            url = "http://www.digikey.com/product-detail/en/x/x/{}".format(
                data['distributor'][self.name()]['distributorPartId'])
        else:
            raise Exception('No valid key found to query for data!')

        if self.partDB.args.debug:
            print('Loading URL %s ...' % url)

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
        productDetails = soup.find_all('table', class_='product-details')
        newData = {
            "distributor": {
                "digikey": {
                    "distributorName": "digikey",
                    "distributorPartNumber": productDetails[0].find_all('td', id="reportpartnumber")[0].get_text().strip(),
                },
            },
            "manufacturerPartNumber": productDetails[0].find_all('h1', itemprop="model")[0].contents[0].strip(),
            "manufacturerName": productDetails[0].find_all('h2', itemprop="manufacturer")[0].contents[0].get_text().strip(),
            "description": productDetails[0].find_all('td', itemprop="description")[0].contents[0].strip()
        }

        # try to get some additional specs
        attributes = soup.find_all('td', class_='attributes-table-main')

        for row in attributes[0].find_all('tr'):
            cells = row.find_all(re.compile("^t[hd]$"))
            if (len(cells) >= 2):
                key = cells[0].get_text().strip()
                val = cells[1].get_text().strip()

                if key == 'Supplier Device Package':
                    newData['manufacturerFootprint'] = val
                elif key == 'Package / Case':
                    newData['footprint'] = val
                elif key == 'Datasheets':
                    val = cells[1].find_all('a')[0]['href']
                    newData['datasheetURL'] = val

        data = copy.copy(data)
        Database.mergeData(data, newData)

        return data
