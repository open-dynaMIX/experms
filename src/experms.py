#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
from parse_arguments import parse_arguments
import configfile.main
from watch.start_pyinotify import start_pyinotify


# global variables
version = "0.1.0"


def debug_message():
    print >> sys.stderr, ("[debug] Argument handling complete")

def main():
    args = parse_arguments()
    print "Experms v" + version
    if args.version:
        sys.exit(0)

    if args.restore:
        if args.debug:
            debug_message()
        config = configfile.main.Check(args.debug)
        sys.exit(0)

    if args.count:
        pass

    if args.debug:
        debug_message()

    config = configfile.main.Check(args.debug)
    start_pyinotify(config.path, args.debug)

    sys.exit(0)

    #handle(args.args)

if __name__ == "__main__":
    main()
