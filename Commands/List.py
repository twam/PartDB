import Commands.__Command


class List(Commands.__Command.Command):

    def __init__(self, partDB):
        super().__init__(partDB)

    @staticmethod
    def getParserHelp():
        return "List all parts."

    def run(self):
        COLUMNS = [
            {
                "label": "PartNumber",
                "data": "manufacturerPartNumber",
                "width": 20,
                "formatter": "s"},
            {
                "label": "Description",
                "data": "description",
                "width": 50,
                "formatter": "s"},
            {
                "label": "Quantity",
                "data": "quantity",
                "width": 10,
                "formatter": "u"},

        ]

        # Header
        print(" | ".join(["%-*s" % (column['width'], column['label'][:column['width']])
                          for column in COLUMNS]))
        print("-|-".join(["-" * (column['width']) for column in COLUMNS]))

        result = self.partDB.db.query()

        # Data
        for key, value in result.items():
            print(" | ".join([("%-*" + column['formatter']) %
                              (column['width'], value[column['data']][:column['width']] if type(value[column['data']]) == str else value[column['data']]) for column in COLUMNS]))

        # Footer
        print("-|-".join(["-" * (column['width']) for column in COLUMNS]))
