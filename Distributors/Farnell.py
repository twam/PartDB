import Distributors.__Distributor
import re
import copy


class Farnell(Distributors.__Distributor.Distributor):

    def __init__(self, partDB):
        super().__init__(partDB)

    def matchPartNumber(self, data):
        if type(data) == str:
            data = data.encode('ascii')

        matches = re.search(
            br'^(?P<distributorPartNumber>\d{7})$', data)
        if matches:
            result = copy.copy(matches.groupdict())
            for key, val in result.items():
                result[key] = val.decode('utf_8')
            return result
        else:
            return None

    def matchBarCode(self, data):
        return None
