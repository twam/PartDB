from .__command import Command
from ..label import Label


class Print(Command):

    def __init__(self, partDB):
        super().__init__(partDB)

    @staticmethod
    def getParserHelp():
        return "Print label for a part."

    @staticmethod
    def configureArgumentSubParser(subparser):
        super(__class__, Print).configureArgumentSubParser(subparser)

        subparser.add_argument('--printer-name',
                               dest='printerName',
                               metavar='printer-name',
                               help="Name of printer to print on.",
                               default='zebra')

        subparser.add_argument('id',
                               type=str,
                               help='Database key to print.')

    def run(self):
        result = self.partDB.db.query(
            filter=lambda k, v: (
                k == self.partDB.args.id))
        if len(result) > 0:
            label = Label()
            label.createLabelFromData(data=result[self.partDB.args.id])
            label.cupsPrint(printerName=self.partDB.args.printerName)
        else:
            raise Exception(
                'ID %s not found in database.' %
                (self.partDB.args.id))
