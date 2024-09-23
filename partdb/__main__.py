#!/usr/bin/env python3

import argparse
import sys
import importlib
import traceback

from pathlib import Path

from .database import Database
from .util import snake_case_to_camel_case


class PartDB:

    def __init__(self, argv):
        self.argv = argv

        self.progname = Path(self.argv[0]).stem

        # Get path of the directory where this file is stored
        self.basePath = Path(__file__).parent

        self._load_commands()
        self._load_distributors()

    def _load_commands(self):
        commands_dir = self.basePath / 'commands'
        self.commands = {}

        for command in commands_dir.iterdir():
            if not command.is_file():
                continue

            if command.stem.startswith('__'):
                continue

            command_name = command.stem.lower()
            class_name = snake_case_to_camel_case(command_name)

            self.commands[command_name] = getattr(
                importlib.import_module('partdb.commands.' + command_name), class_name)(self)

    def _load_distributors(self):
        distributors_dir = self.basePath / 'distributors'
        self.distributors = {}

        for distributor in distributors_dir.iterdir():
            if not distributor.is_file():
                continue

            if distributor.stem.startswith('__'):
                continue

            distributor_name = distributor.stem.lower()
            class_name = snake_case_to_camel_case(distributor_name)

            self.distributors[distributor_name] = getattr(
                importlib.import_module('partdb.distributors.' + distributor_name), class_name)(self)

    def parse_arguments(self):

        parser = argparse.ArgumentParser(
            description='PartDB',
            prog=self.progname,
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            fromfile_prefix_chars='@')

        parser.add_argument("-h", "--help",
                            action="help",
                            help="Show this help message and exit.")

        parser.add_argument("--version",
                            action="version",
                            help="Show the version and exit.",
                            version="0.1")

        parser.add_argument("-v", "--verbose",
                            action="store_true",
                            dest="verbose",
                            help="Be verbose.")

        parser.add_argument('-d', '--database',
                            help='Specify database filename.',
                            dest='databaseFilename',
                            default='partdb.json',
                            metavar='database')

        parser.add_argument('--debug',
                            help='print debug information',
                            dest='debug',
                            action='store_true')

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
                if (key in self.db.SCHEMA) and (
                        'formatter' in self.db.SCHEMA[key]):
                    print("%-30s: %s" %
                          (key, self.db.SCHEMA[key]['formatter'](data[key])))
                else:
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
        self.parse_arguments()

        # open database
        self.db = Database(self.args.databaseFilename)

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

def main():
    PartDB(sys.argv).run()

if __name__ == '__main__':
    main()
