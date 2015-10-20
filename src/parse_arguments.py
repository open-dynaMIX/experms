#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import sys


class ParseArgs(object):
    """Parse CLI-arguments"""
    def __init__(self):
        self.parser = argparse.ArgumentParser(description=sys.argv[0],
                                 formatter_class=argparse.
                                 RawDescriptionHelpFormatter)

        self.parser.add_argument("-d", "--debug", dest="debug",
                                  action="store_true", help="Print debug-"
                                  "messages.")

        self.parser.add_argument("-r", "--restore", dest="restore",
                                  action="store_true", help="Just restore all "
                                  "the permissions and exit.")

        self.parser.add_argument("-v", "--version", dest="version",
                                  action="store_true", help="Print the version "
                                  "and exit.")

        self.parser.add_argument("-c", "--count", dest="count",
                                  action="store_true", help="Count the "
                                  "directories to watch and exit.")

        self.args = self.parser.parse_args()
