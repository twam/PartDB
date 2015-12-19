import Distributors.__Distributor
import re
import copy
import urllib.request
import bs4


class Mouser(Distributors.__Distributor.Distributor):

    def __init__(self, partDB):
        super().__init__(partDB)

    def matchPartNumber(self, data):
        if type(data) == str:
            data = data.encode('ascii')

        matches = re.search(
            br'^(?P<distributorPartNumber>\d{2,3}-([-A-Z0-9.]+?(?<!-ND)))$', data)
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
            br'^>\[\)>(06)(\x1d[0-9]{0,2}[KPQL][-A-Z0-9,]+)+$', data)
        if matches:
            groups = re.findall(br'(\x1d)([0-9]{0,2})([KPQL])([-A-Z0-9,]+)', data)
            result = {}
            for group in groups:
                if group[1] == b'1' and group[2] == b'P':
                    result['manufacturerPartNumber'] = group[3].decode('utf_8')
                elif group[1] == b'' and group[2] == b'Q':
                    result['quantity'] = int(group[3].decode('ascii'))
            return result
        else:
            return None

    def getData(self, distributorPartNumber):

        data = None

        url = "http://www.mouser.com/Search/Refine.aspx?Keyword={}".format(distributorPartNumber)
        req = urllib.request.Request(url, headers={'User-Agent' : "electronic-parser"})
        page = urllib.request.urlopen(req)
        soup = bs4.BeautifulSoup(page.read(), 'html.parser')

        # basic data
        productDesc = soup.find_all('div', id='product-desc')
        data = {
            "distributor": {
                "mouser": {
                    "distributorName": "mouser",
                    "distributorPartNumber": distributorPartNumber,
                }
            },
            "manufacturerPartNumber": productDesc[0].find_all('div', itemprop="ProductID")[0].contents[1].contents[1].contents[0].strip(),
            "description": productDesc[0].find_all('span', itemprop="description")[0].contents[1].contents[0].strip()
        }

        # try to get some additional specs
        specs = soup.find_all('div', id='specs')

        for row in specs[0].find_all('tr', class_=lambda x: x == "odd" or x == "even"):
            cells = row.find_all("td")
            key = cells[0].get_text().strip()
            val = cells[1].get_text().strip()

            if key == 'Manufacturer:':
                data['manufacturerName'] = val
            elif key == 'Package/Case:':
                data['footprint'] = val

        return data
