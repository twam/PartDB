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

        # Load all actions
        actionsDir = os.path.join(self.basePath, 'Actions')
        self.actions = {}
        for action in os.listdir(actionsDir):
            matches = re.match(r'(([A-Za-z]+)\.py)', action)
            if matches:
                actionName = matches.groups()[1].lower()
                moduleName = matches.groups()[0]
                className = matches.groups()[1]

                self.actions[actionName] = getattr(
                    importlib.import_module('Actions.' + className), className)

    def parseArguments(self):

        def ActionArgument(v):
            if v not in self.actions:
                raise argparse.ArgumentTypeError(
                    "%s is not a valid action." % (v))
            else:
                return v

        parser = argparse.ArgumentParser(
            description='PartDB', prog=self.argv[0])

        subparsers = parser.add_subparsers(help='Action', dest='action')
        subparsers.required = True

        for actionName in sorted([key for key in self.actions.keys()]):
            actionClass = self.actions[actionName]
            subparser = subparsers.add_parser(
                actionName, help=actionClass.getParserHelp())
            actionClass.configureArgumentSubParser(subparser)

        # parser.add_argument('action', type=ActionArgument,
        # help='Action to perform. Allowed actions are %s.' % (",
        # ".join(sorted([key for key in self.actions.keys()]))))

        self.args = parser.parse_args(self.argv[1:])

    def run(self):
        self.parseArguments()

        # open database
        self.db = Database.Database('partdb.json')

        # call requested action
        action = self.actions[self.args.action](self)
        action.run()

if __name__ == '__main__':
    PartDB(sys.argv).run()
