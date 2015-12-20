#!/usr/bin/env python3

import argparse
import sys
import importlib
import inspect
import re
import os
import traceback
import Database


class PartDB:

    def __init__(self, argv):
        self.argv = argv

        self.progname = os.path.basename(self.argv[0])

        # Get path of the directory where this file is stored
        self.basePath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))

        self._loadCommands()
        self._loadDistributors()

    def _loadCommands(self):
        commandsDir = os.path.join(self.basePath, 'Commands')
        self.commands = {}
        for command in os.listdir(commandsDir):
            matches = re.match(r'(((?!test)[A-Za-z]+)\.py)', command)
            if matches:
                commandName = matches.groups()[1].lower()
                className = matches.groups()[1]

                self.commands[commandName] = getattr(
                    importlib.import_module('Commands.' + className), className)(self)

    def _loadDistributors(self):
        distributorsDir = os.path.join(self.basePath, 'Distributors')
        self.distributors = {}
        for distributor in os.listdir(distributorsDir):
            matches = re.match(r'(((?!test)[A-Za-z]+)\.py)', distributor)
            if matches:
                distributorName = matches.groups()[1].lower()
                className = matches.groups()[1]

                self.distributors[distributorName] = getattr(
                    importlib.import_module('Distributors.' + className), className)(self)

    def parseArguments(self):

        parser = argparse.ArgumentParser(
            description='PartDB', prog=self.progname, add_help=False)
        parser.add_argument("-h", "--help", action="help",
                            help="Show this help message and exit.")

        parser.add_argument("--version", action="version",
                            help="Show the version and exit.", version="0.1")

        parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                            help="Be verbose.")

        parser.add_argument('-d', '--database', help='Specify database filename.',
                            dest='databaseFilename', default='partdb.json', metavar='database')

        parser.add_argument('--debug', help='print debug information',
                            dest='debug', action='store_true')

        subparsers = parser.add_subparsers(
            help='Command to execute. See \'%s command -h\' for help on specific commands. The following commands are implemented:' % (self.progname), dest='command', metavar='command')
        subparsers.required = True

        for commandName in sorted([key for key in self.commands.keys()]):
            commandClass = self.commands[commandName]
            subparser = subparsers.add_parser(
                commandName, help=commandClass.getParserHelp(), add_help=False)
            commandClass.configureArgumentSubParser(subparser)

        self.args = parser.parse_args(self.argv[1:])

    def displayList(self, data, showIds=False):
        COLUMNS = [
            {
                "label": "Part Number",
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

        if showIds == True:
            COLUMNS.insert(0, {
                "label": "ID",
                "data": "key",
                "width": 36,
                "formatter": "s"})

        # Header
        print(" | ".join(["%-*s" % (column['width'], column['label'][:column['width']])
                          for column in COLUMNS]))
        print("-|-".join(["-" * (column['width']) for column in COLUMNS]))

        # Data
        for key, value in data.items():
            print(" | ".join([("%-*" + column['formatter']) %
                              (column['width'], key if column['data'] == 'key' else value[column['data']][:column['width']] if isinstance(value[column['data']], str) else value[column['data']]) for column in COLUMNS]))

        # Footer
        print("-|-".join(["-" * (column['width']) for column in COLUMNS]))

    def displayItem(self, data, showKey=False):
        print("--- General ---")
        for key in sorted(data.keys()):
            if key != 'distributor':
                print("%-30s: %s" % (key, data[key]))

        if 'distributor' in data:
            for distributorName in sorted(data['distributor'].keys()):
                print("--- Distributor: %s ---" % (distributorName))
                for key2 in sorted(data['distributor'][
                                   distributorName].keys()):
                    print(
                        "%-30s: %s" %
                        (key2, data['distributor'][distributorName][key2]))

    def run(self):
        self.parseArguments()

        # open database
        self.db = Database.Database(self.args.databaseFilename)

        # call requested command
        command = self.commands[self.args.command]
        try:
            command.run()
        except Exception as e:
            if (self.args.debug):
                traceback.print_exc()
            if (len(e.args) > 0):
                sys.exit(e.args[0])
            else:
                sys.exit("Unknown error: %s" % sys.exc_info()[0])

if __name__ == '__main__':
    PartDB(sys.argv).run()
