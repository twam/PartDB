import Commands.__Command


class List(Commands.__Command.Command):

    def __init__(self, partDB):
        super().__init__(partDB)

    @staticmethod
    def getParserHelp():
        return "List all parts."

    @staticmethod
    def configureArgumentSubParser(subparser):
        super(__class__, List).configureArgumentSubParser(subparser)
        subparser.add_argument('-o', '--order-by', help='Order results by a specific field.',
                               dest='orderBy', metavar='order-by', default='manufacturerPartNumber')
        subparser.add_argument('-k', '--keys', help='Show database keys for results',
                               dest='showKeys', action='store_true')

    def run(self):
        self.partDB.displayList(self.partDB.db.query(
            orderBy=self.partDB.args.orderBy), showKeys=self.partDB.args.showKeys)
