from . import __Distributor
import re
import copy
import urllib.request
import bs4
import Database
import urllib.parse


class Mouser(__Distributor.Distributor):
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

    def getData(self, data):
        newData = None

        if 'distributorPartNumber' in data['distributor'][self.name()]:
            url = "http://www.mouser.com/Search/Refine.aspx?Keyword={}".format(
                data['distributor'][self.name()]['distributorPartNumber'])
        else:
            raise Exception('No valid key found to query for data!')

        if self.partDB.args.debug:
            print('Loading URL %s ...' % url)

        req = urllib.request.Request(
            url, headers={'User-Agent': "electronic-parser"})
        page = urllib.request.urlopen(req)
        soup = bs4.BeautifulSoup(page.read(), 'html5lib')

        searchResults = soup.find_all('div', id='searchResultsTbl')
        if searchResults != []:
            if self.partDB.args.debug:
                print('Found search results on paging. Trying to find correct part.')

            for row in searchResults[0].find_all(
                    'tr', class_=lambda x: x == "SearchResultsRowOdd" or x == "SearchResultsRowEven"):

                if row['data-partnumber'] == data['distributor'][self.name()
                                                                 ]['distributorPartNumber']:

                    cols = row.find_all('td')
                    link_col = cols[2]
                    newRelUrl = link_col.find_all('a')[0]['href']
                    newUrl = urllib.parse.urljoin(url, newRelUrl)

                    if self.partDB.args.debug:
                        print('Part found! Loading new URL %s ...' % newUrl)

                    req = urllib.request.Request(
                        newUrl, headers={'User-Agent': "electronic-parser"})
                    page = urllib.request.urlopen(req)
                    soup = bs4.BeautifulSoup(page.read(), 'html5lib')

                    break

            if newUrl is None:
                raise Exception("Did not find part in search results")

        # basic data
        productDesc = soup.find_all('div', id='product-desc')
        newData = {
            "distributor": {
                "mouser": {
                    "distributorName": "mouser",
                    "distributorPartNumber": productDesc[0].find_all('div', itemprop="model")[0].get_text().strip(),
                }
            },
            "manufacturerPartNumber": productDesc[0].find_all('div', itemprop="ProductID")[0].get_text().strip(),
            "description": productDesc[0].find_all('span', itemprop="description")[0].get_text().strip()
        }

        # try to get some additional specs
        specs = soup.find_all('div', id='specs')

        for row in specs[0].find_all(
                'tr', class_=lambda x: x == "odd" or x == "even"):
            cells = row.find_all("td")
            key = cells[0].get_text().strip()
            val = cells[1].get_text().strip()

            if key == 'Manufacturer:':
                newData['manufacturerName'] = val
            elif key == 'Package/Case:':
                newData['footprint'] = val

        data = copy.copy(data)
        Database.mergeData(data, newData)

        return data
