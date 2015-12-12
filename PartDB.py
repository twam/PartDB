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
            description='PartDB', prog=self.argv[0])

        subparsers = parser.add_subparsers(help='Command', dest='command')
        subparsers.required = True

        for commandName in sorted([key for key in self.commands.keys()]):
            commandClass = self.commands[commandName]
            subparser = subparsers.add_parser(
                commandName, help=commandClass.getParserHelp())
            commandClass.configureArgumentSubParser(subparser)

        self.args = parser.parse_args(self.argv[1:])

    def run(self):
        self.parseArguments()

        # open database
        self.db = Database.Database('partdb.json')

        # call requested command
        command = self.commands[self.args.command](self)
        command.run()

if __name__ == '__main__':
    PartDB(sys.argv).run()
