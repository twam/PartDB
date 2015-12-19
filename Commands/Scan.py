import Commands.__Command
import Database
import collections
import serial
import select
import sys


class Scan(Commands.__Command.Command):

    def __init__(self, partDB):
        super().__init__(partDB)

    @staticmethod
    def getParserHelp():
        return "Scan a part."

    @staticmethod
    def configureArgumentSubParser(subparser):
        super(__class__, Scan).configureArgumentSubParser(subparser)

        subparser.add_argument('-d', '--device', dest='device',
                               metavar='device', required=True, help='Device to scan from.')

        subparser.add_argument('--confirm-quantity', dest='confirmQuantity',
                               action='store_true', help='Confirm quantity before adding to database.')

        subparser.add_argument('--print-label', dest='printLabel', action='store_true',
                               help='Print label for item after adding to database.')

        # subparser.add_argument('data', nargs='+', default=[],
        #                        type=str, help='Scanned data.')

    def scan(self):
        ser = serial.Serial(self.partDB.args.device, timeout=0.05)
        ser.flushInput()

        while True:
            data = ser.read(1000)

            if len(data) > 0:
                break

        ser.close()

        return(data)

    def scanAndInput(self):
        ser = serial.Serial(self.partDB.args.device, timeout=0.05)
        ser.flushInput()

        while True:
            i, o, e = select.select([sys.stdin], [], [], 0.05)
            serialData = ser.read(1000)

            if (i):
                keyboardData = sys.stdin.readline()[:-1].encode('utf_8')
                return keyboardData

            if len(serialData) > 0:
                print(serialData.decode('utf_8'))
                ser.close()
                return serialData

    def run(self):
        print('Scan/Enter Barcode/PN:')

        data = self.scanAndInput()

        # search distributors
        distributorMatches = {}

        for distributorName, distributor in self.partDB.distributors.items():
            distributorMatches[distributorName] = {}

            distributorMatches[distributorName][
                'barCode'] = distributor.matchBarCode(data)
            distributorMatches[distributorName][
                'manufacturerPartNumber'] = distributor.matchPartNumber(data)

        # print table if verbose
        if (self.partDB.args.verbose):
            for distributorName in sorted(distributorMatches.keys()):
                print("%-10s %c %c" % (
                    self.partDB.distributors[distributorName].name(),
                    'X' if distributorMatches[
                        distributorName]['barCode'] else '-',
                    'X' if distributorMatches[distributorName]['manufacturerPartNumber'] else '-'))

        # count number of distributor matches
        count = 0
        distributorName = None
        for key in sorted(distributorMatches.keys()):
            if distributorMatches[key]['barCode'] or distributorMatches[key]['manufacturerPartNumber']:
                count += 1
                distributorName = key

        # check if we have exactly one result
        if (count > 1):
            raise Exception('More than one distributor matched data!')
        elif (count == 0):
            raise Exception('No distributor matched data!')
        else:
            pass

        # get more data
        data = {}

        if distributorMatches[distributorName]['barCode']:
            Database.mergeData(data, distributorMatches[distributorName][
                               'barCode'], override=True)
        if distributorMatches[distributorName]['manufacturerPartNumber']:
            Database.mergeData(data, distributorMatches[distributorName][
                               'manufacturerPartNumber'], override=True)

        data = self.partDB.distributors[distributorName].getData(data)

        # Ask for quantity if not there
        if 'quantity' not in data:
            print('Scan/Enter Quantity:')
            data['quantity'] = int(self.scanAndInput())
        elif self.partDB.args.confirmQuantity:
            print('Quantity is %u. Scan/Enter new quantity or press return:' %
                  data['quantity'])
            quantityInput = self.scanAndInput()
            if quantityInput != b'':
                data['quantity'] = int(quantityInput.decode('ascii'))

        self.partDB.displayItem(data)

        # check for partnumber
        if 'manufacturerPartNumber' not in data:
            raise Exception('No manufacturerPartNumber!')

        res = self.partDB.db.query(filter=lambda k, v: (
            v['manufacturerPartNumber'] == data['manufacturerPartNumber']))
        if len(res) > 0:
            raise Exception('Part already in DB!')

        # Add part to database
        partKey = self.partDB.db.add(data)
        print('Added with key %s.' % partKey)

        if (self.partDB.args.printLabel):
            print('Here a label should be printed. :P')
