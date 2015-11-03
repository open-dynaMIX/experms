# -*- coding: utf-8 -*-

import argparse
import sys


def parse_arguments():
      parser = argparse.ArgumentParser(description=sys.argv[0],
                               formatter_class=argparse.
                               RawDescriptionHelpFormatter)

      parser.add_argument("-c", "--config", dest="config",
                              help="Configuration file to use.")
      parser.set_defaults(command=None)

      parser.add_argument("-r", "--restore", dest="restore",
                                action="store_true", help="Just restore all "
                                "the permissions and exit.")

      parser.add_argument("-t", "--total", dest="total",
                                action="store_true", help="Count the "
                                "directories to watch and exit.")

      parser.add_argument("-v", "--version", dest="version",
                                action="store_true", help="Print the version "
                                "and exit.")

      parser.add_argument("-d", "--debug", dest="debug",
                                action="store_true", help="Print debug-"
                                "messages.")

      args = parser.parse_args()

      return args
