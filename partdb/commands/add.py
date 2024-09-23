from .__command import Command

from ..database import Database
import collections


class Add(Command):

    def __init__(self, partDB):
        super().__init__(partDB)

    @staticmethod
    def getParserHelp():
        return "Add a part."

    @staticmethod
    def configureArgumentSubParser(subparser):
        super(__class__, Add).configureArgumentSubParser(subparser)

        for key, val in Database.SCHEMA.items():
            if 'argument' in val:
                subparser.add_argument(*[x for x in [val['argument'], '--%s' % (key)] if x is not None],
                                       dest=key,
                                       metavar=key,
                                       default=val['default'],
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
        partData = {}

        for key, val in Database.SCHEMA.items():
            if 'argument' in val:
                partData[key] = vars(self.partDB.args)[key]

        distributor = collections.defaultdict(dict)
        for key, val in Database.KEYS_DISTRIBUTOR.items():
            if 'argument' in val:
                pos = 0
                data = vars(self.partDB.args)[key]
                for pos in range(0, len(data)):
                    distributor[pos][key] = data[pos]

        # rename distributor keys
        partData['distributor'] = {}
        for key, val in distributor.items():
            if 'distributorName' in val:
                partData['distributor'][val['distributorName']] = val
            else:
                raise Exception('No distributor name set for data %s' % val)

        self.partDB.db.add(partData)
