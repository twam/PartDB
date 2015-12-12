class Action():

    def __init__(self, partDB):
        self.partDB = partDB

    @staticmethod
    def getParserHelp():
        return ""

    @staticmethod
    def configureArgumentSubParser(subparser):
        pass

    def run(self):
        raise Exception('Action not defined')
