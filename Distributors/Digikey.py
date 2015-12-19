import Distributors.__Distributor
import re
import copy
import bs4
import urllib


class Digikey(Distributors.__Distributor.Distributor):

    def __init__(self, partDB):
        super().__init__(partDB)

    def matchPartNumber(self, data):
        if type(data) == str:
            data = data.encode('ascii')

        matches = re.search(
            br'^(?P<distributorPartNumber>[-+A-Z0-9]+-ND)$', data)
        if matches:
            result = copy.copy(matches.groupdict())
            for key,val in result.items():
                result[key] = val.decode('utf_8')
            return result
        else:
            return None

    def matchBarCode(self, data):
        if type(data) == str:
            data = data.encode('ascii')

        matches = re.search(
            br'^(?P<distributorPartId>\d{7})(?P<quantity>\d{9})(\d{6})$', data)
        if matches:
            result = copy.copy(matches.groupdict())
            for key,val in result.items():
                result[key] = val.decode('utf_8')
            result['quantity'] = int(result['quantity'])
            return result
        else:
            return None

    def getData(self, distributorPartNumber):
        data = None

        url = "http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail&name={}".format(distributorPartNumber)
        req = urllib.request.Request(url, headers={'User-Agent' : "electronic-parser"})
        page = urllib.request.urlopen(req)
        soup = bs4.BeautifulSoup(page.read(), 'html.parser')

        # basic data
        productDetails = soup.find_all('table', class_='product-details')
        data = {
            "distributor": {
                "digikey": {
                    "distributorName": "digikey",
                    "distributorPartNumber": distributorPartNumber,
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
                    data['footprint'] = val
                elif key == 'Datasheets':
                    val = cells[1].find_all('a')[0]['href']
                    data['datasheetURL'] = val

        return data

