from .__command import Command
from ..database import Database


class Update(Command):

    def __init__(self, partDB):
        super().__init__(partDB)

    @staticmethod
    def getParserHelp():
        return "Update a part."

    @staticmethod
    def configureArgumentSubParser(subparser):
        super(__class__, Update).configureArgumentSubParser(subparser)

        for key, val in Database.SCHEMA.items():
            if 'argument' in val:
                subparser.add_argument(*[x for x in [val['argument'], '--%s' % (key)] if x is not None],
                                       dest=key,
                                       metavar=key,
                                       type=val['type'],
                                       help=val['help'])

        for key, val in Database.KEYS_DISTRIBUTOR.items():
            if 'argument' in val:
                subparser.add_argument(*[x for x in [val['argument'], '--%s' % (key)] if x is not None],
                                       dest=key,
                                       metavar=key,
                                       default=[],
                                       type=val['type'],
                                       help=val['help'],
                                       action='append')

    def run(self):
        raise Exception('Not implemented.')
        # self.partDB.db.update('4203f26e-0c6f-426c-8d22-d321729714d4', {
        #                       "quantity": 15, "manufacturerPartNumber": "test2", "description": "blub"})
