#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os
from procname import set_procname
from parse_arguments import parse_arguments
import configfile.main
from watch.start_pyinotify import start_pyinotify
from restore.main import restore
from restore.collect_filenames import collect


# global variables
version = "0.1.0"


def debug_message():
    print >> sys.stderr, ("[debug] Argument handling complete")

def main():
    if not os.geteuid() == 0:
        print >> sys.stderr, ("You need to run experms with root privileges."
                              "\nAborting.")
        sys.exit(1)

    set_procname("experms")

    args = parse_arguments()

    try:
        if os.environ['SYSTEMD_LOG_LEVEL'] == "debug":
            args.debug = True
    except KeyError:
        pass

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
        if args.debug:
            debug_message()
        config = configfile.main.Check(args.debug)
        print ("Directories configured for watching:\n%s"
               % len(collect(config)[0]))
        with open('/proc/sys/fs/inotify/max_user_watches', 'r') as inotifyconf:
            inotifyconfig = inotifyconf.read().strip()
        print ("Directories allowed to watch with inotify:\n%s"
               % inotifyconfig)
        sys.exit(0)

    if args.debug:
        debug_message()

    config = configfile.main.Check(args.debug)

    if config.restore:
        if args.debug:
            print >> sys.stderr, ("[debug] Starting restore")
        restore(config, args.debug)

    start_pyinotify(config, args.debug)

    sys.exit(0)


if __name__ == "__main__":
    main()
