import Commands.__Command
import re


class Search(Commands.__Command.Command):

    def __init__(self, partDB):
        super().__init__(partDB)

    @staticmethod
    def getParserHelp():
        return "Search for specific parts."

    @staticmethod
    def configureArgumentSubParser(subparser):
        super(Search, Search).configureArgumentSubParser(subparser)
        subparser.add_argument('pattern', type=str, help='search pattern')
        subparser.add_argument(
            '-r', '--regex', help='Interpret search pattern as regular expression.', action='store_true', dest='regex')
        subparser.add_argument(
            '-i', '--ignore-case', help='Perform case insensitive matching.', action='store_true', dest='ignoreCase')
        subparser.add_argument('-f', '--fields', nargs='+', help='List of fields to search in.',
                               dest='fields', default=['manufacturerPartNumber', 'description'])
        subparser.add_argument('-o', '--order-by', help='Order results by a specific field.',
                               dest='orderBy', metavar='order-by', default='manufacturerPartNumber')

    def __query_filter(self, key, val):
        for field in self.partDB.args.fields:
            regex = self.partDB.args.pattern if self.partDB.args.regex == True else re.escape(
                args.pattern)
            if re.search(regex, str(val[field]), flags=re.IGNORECASE if self.partDB.args.ignoreCase else 0):
                return True

        return False

    def run(self):
        self.partDB.displayList(self.partDB.db.query(
            filter=self.__query_filter, orderBy=self.partDB.args.orderBy))
