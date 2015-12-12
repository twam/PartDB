class Command():

    def __init__(self, partDB):
        self.partDB = partDB

    @staticmethod
    def getParserHelp():
        return ""

    @staticmethod
    def configureArgumentSubParser(subparser):
        subparser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")

    def run(self):
        raise Exception('Command not defined')
