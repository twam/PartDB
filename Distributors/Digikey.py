import Distributors.__Distributor
import re
import copy


class Digikey(Distributors.__Distributor.Distributor):

    def __init__(self, partDB):
        super().__init__(partDB)

    def matchPartNumber(self, data):
        matches = re.search(
            '^(?P<distributorPartNumber>[-+A-Z0-9]+-ND)$', data)
        if matches:
            result = copy.copy(matches.groupdict())
            return result
        else:
            return None

    def matchBarcode(self, data):
        matches = re.search(
            '^(?P<distributorPartId>\d{7})(?P<quantity>\d{8})(\d{6})$', data)
        if matches:
            result = copy.copy(matches.groupdict())
            result['quantity'] = int(result['quantity'])
            return result
        else:
            return None
