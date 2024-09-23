from .__command import Command
from ..database import Database
from ..label import Label

import serial
import select
import sys
import re
import copy


class Scan(Command):

    def __init__(self, partDB):
        super().__init__(partDB)

    @staticmethod
    def getParserHelp():
        return "Scan a part."

    @staticmethod
    def configureArgumentSubParser(subparser):
        super(__class__, Scan).configureArgumentSubParser(subparser)

        subparser.add_argument('-d', '--device',
                               dest='device',
                               metavar='device',
                               required=True,
                               help='Device to scan from.')

        subparser.add_argument('--confirm-quantity',
                               dest='confirmQuantity',
                               action='store_true',
                               help='Confirm quantity before adding item to database.')

        subparser.add_argument('--print-label',
                               dest='printLabel',
                               action='store_true',
                               help='Print label for item after adding it to database.')

        subparser.add_argument('--printer-name',
                               dest='printerName',
                               metavar='printer-name',
                               help="Name of printer to print on.",
                               default='zebra')

        subparser.add_argument('--fix',
                               dest='fix',
                               action='store_true',
                               help='Try to fix database information.')

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

    def handleScannedPartId(self, partId):
        result = self.partDB.db.query(
            filter=lambda k, v: (
                k == partId))

        if len(result) == 0:
            raise Exception('Part ID %s not found in database.' % (partId))

        if self.partDB.args.fix:
            result = self.partDB.db.query(
                filter=lambda k, v: (
                    k == partId))
            data = result[partId]

            distributorMatches = {}
            for distributorName in data['distributor']:
                minimumData = {
                    'distributor': {
                        distributorName: {
                            'distributorPartNumber': data['distributor'][distributorName]['distributorPartNumber']
                        }
                    }
                }

                newData = self.partDB.distributors[
                    distributorName].getData(minimumData)

                Database.mergeData(data, newData, override=True)

            self.partDB.db.update(data)

            if len(result) > 0:
                if (self.partDB.args.printLabel):
                    label = Label()
                    label.createLabelFromData(data=data)
                    label.cupsPrint(printerName=self.partDB.args.printerName)
            else:
                raise Exception(
                    'ID %s not found in database.' %
                    (self.partDB.args.id))

            return

        data = result[partId]

        self.partDB.displayItem(data)

        print('Quantity is %u. Scan/Enter new quantity (+/- for relative) or press return:' %
              data['quantity'])
        quantityInput = self.scanAndInput()
        if quantityInput != b'':
            quantityInputAscii = quantityInput.decode('ascii')
            # check if first character is + or -
            if (quantityInputAscii[0]
                ) == '+' or (quantityInputAscii[0] == '-'):
                data['quantity'] += int(quantityInputAscii)
            else:
                data['quantity'] = int(quantityInputAscii)

            print('New quantity is %u.' % (data['quantity']))
            self.partDB.db.update(data)

    def handleScannedNonPartId(self, data):
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
            if distributorMatches[key]['barCode'] or distributorMatches[
                    key]['manufacturerPartNumber']:
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

        # Assure that all types are correct
        self.partDB.db.assureTypes(data)

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

        return

        res = self.partDB.db.query(filter=lambda k, v: (
            v['manufacturerPartNumber'] == data['manufacturerPartNumber']))
        if len(res) > 0:
            id_ = (list(res.keys()))[0]
            print(
                'Part already found in database with ID %s. Adding quantity.' %
                id_)
            oldData = copy.copy(res[id_])
            oldData['quantity'] += data['quantity']

            self.partDB.db.update(oldData)
            return

        # Add part to database
        data = self.partDB.db.add(data)
        print('Added with key %s.' % data['id'])

        if (self.partDB.args.printLabel):
            label = Label.Label()
            label.createLabelFromData(data=data)
            label.cupsPrint(printerName=self.partDB.args.printerName)

    def run(self):
        print('Scan/Enter Barcode/PN:')

        data = self.scanAndInput()

        if (re.match(
                b'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$', data)):
            self.handleScannedPartId(data.decode('ascii'))
        else:
            self.handleScannedNonPartId(data)
