class Command():

    def __init__(self, partDB):
        self.partDB = partDB

    @staticmethod
    def getParserHelp():
        return ""

    @staticmethod
    def configureArgumentSubParser(subparser):
        pass

    def run(self):
        raise Exception('Command not defined')
