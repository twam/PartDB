import Actions.__Action


class List(Actions.__Action.Action):

    def __init__(self, partDB):
        super().__init__(partDB)

    def run(self):
        for item in self.partDB.db:

            print(item, self.partDB.db[item])
