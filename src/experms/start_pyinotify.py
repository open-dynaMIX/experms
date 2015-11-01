# -*- coding: utf-8 -*-

import sys
import time
from event_handler import EventHandler
try:
    import pyinotify
except ImportError:
    print >> sys.stderr, ("Error: Module pyinotify not found. Please"
                          "install the package 'python2-pyinotify'.\nMaybe "
                          "this package is called differently in your "
                          "distribution (e.g. python2.7-pyinotify).")
    sys.exit(1)


def start_pyinotify(config, debug):
    """
    Start pyinotify
    """
    # do not use IN_MOVED_SELF! It will burn down your house!
    mask = (pyinotify.IN_CREATE | pyinotify.IN_MODIFY |
            pyinotify.IN_ATTRIB | pyinotify.IN_MOVED_TO) # watched events

    # watch manager
    wm = pyinotify.WatchManager()
    notifier = pyinotify.ThreadedNotifier(wm, EventHandler(config, debug))

    # Start the notifier from a new thread, without doing anything as no
    # directory or file is currently monitored yet.
    notifier.start()
    # Start watching the paths
    wdd = wm.add_watch(config.path, mask, rec=True, auto_add=True)

    if debug:
        print >> sys.stderr, ("[debug] Start to watch files")

    try:
        while True:
            time.sleep(0.05)
    except KeyboardInterrupt:
        # happens when the user presses ctrl-c
        wm.rm_watch(wdd.values())
        notifier.stop()
        print "\nBye-bye!"
        sys.exit(0)
    except EOFError:
        # happens when the user presses ctrl-d
        wm.rm_watch(wdd.values())
        notifier.stop()
        print "\nBye-bye!"
        sys.exit(0)

