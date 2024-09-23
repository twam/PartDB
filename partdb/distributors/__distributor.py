class Distributor:

    def __init__(self, partDB):
        self.partDB = partDB

    def name(self):
        return self.__class__.__name__.lower()

    def matchPartNumber(self, data):
        return None

    def matchBarCode(self, data):
        return None

    def getData(self, distributorPartNumber):
        return None
