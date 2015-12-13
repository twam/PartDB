import Commands.__Command


class Delete(Commands.__Command.Command):

    def __init__(self, partDB):
        super().__init__(partDB)

    @staticmethod
    def getParserHelp():
        return "Delete a part."

    @staticmethod
    def configureArgumentSubParser(subparser):
        super(__class__, Delete).configureArgumentSubParser(subparser)

        subparser.add_argument('key', type=str, help='Database key to delete.')

    def run(self):
        if self.partDB.args.key in self.partDB.db:
            self.partDB.db.delete(self.partDB.args.key)
        else:
            raise Exception('Key \'%s\' not found in database.' %
                            (self.partDB.args.key))
