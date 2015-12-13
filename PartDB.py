#!/usr/bin/env python3

import argparse
import sys
import importlib
import inspect
import re
import os
import Database


class PartDB:

    def __init__(self, argv):
        self.argv = argv

        self.progname = os.path.basename(self.argv[0])

        # Get path of the directory where this file is stored
        self.basePath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))

        # Load all commands
        commandsDir = os.path.join(self.basePath, 'Commands')
        self.commands = {}
        for command in os.listdir(commandsDir):
            matches = re.match(r'(([A-Za-z]+)\.py)', command)
            if matches:
                commandName = matches.groups()[1].lower()
                moduleName = matches.groups()[0]
                className = matches.groups()[1]

                self.commands[commandName] = getattr(
                    importlib.import_module('Commands.' + className), className)

    def parseArguments(self):

        parser = argparse.ArgumentParser(
            description='PartDB', prog=self.progname, add_help=False)
        parser.add_argument("-h", "--help", action="help",
                            help="Show this help message and exit.")

        parser.add_argument("-v", "--version", action="version",
                            help="Show the version and exit.", version="0.1")

        parser.add_argument('-d', '--database', help='Specify database filename.',
                            dest='databaseFilename', default='partdb.json', metavar='database')

        subparsers = parser.add_subparsers(
            help='Command to execute. See \'%s command -h\' for help on specific commands. The following commands are implemented:' % (self.progname), dest='command', metavar='command')
        subparsers.required = True

        for commandName in sorted([key for key in self.commands.keys()]):
            commandClass = self.commands[commandName]
            subparser = subparsers.add_parser(
                commandName, help=commandClass.getParserHelp(), add_help=False)
            commandClass.configureArgumentSubParser(subparser)

        self.args = parser.parse_args(self.argv[1:])

    def displayList(self, data):
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

        # Data
        for key, value in data.items():
            print(" | ".join([("%-*" + column['formatter']) %
                              (column['width'], value[column['data']][:column['width']] if type(value[column['data']]) == str else value[column['data']]) for column in COLUMNS]))

        # Footer
        print("-|-".join(["-" * (column['width']) for column in COLUMNS]))

    def run(self):
        self.parseArguments()

        # open database
        self.db = Database.Database(self.args.databaseFilename)

        # call requested command
        command = self.commands[self.args.command](self)
        command.run()

if __name__ == '__main__':
    PartDB(sys.argv).run()
