#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os
from parse_arguments import parse_arguments
import configfile.main
from watch.start_pyinotify import start_pyinotify
from restore.main import restore


# global variables
version = "0.1.0"


def debug_message():
    print >> sys.stderr, ("[debug] Argument handling complete")

def main():
    if not os.geteuid() == 0:
        print >> sys.stderr, ("You need to run experms with root privileges."
                              "\nAborting.")
        sys.exit(1)

    args = parse_arguments()

    if args.version:
        print "Experms v" + version
        sys.exit(0)

    if args.restore:
        if args.debug:
            debug_message()
        config = configfile.main.Check(args.debug)
        restore(config, args.debug)

        sys.exit(0)

    if args.count:
        pass

    if args.debug:
        debug_message()

    config = configfile.main.Check(args.debug)
    start_pyinotify(config, args.debug)

    sys.exit(0)

    #handle(args.args)

if __name__ == "__main__":
    main()
