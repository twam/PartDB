class Distributor:

    def __init__(self, partDB):
        self.partDB = partDB

    def name(self):
        return self.__class__.__name__

    def matchPartNumber(self, data):
        return None

    def matchBarcode(self, data):
        return None
