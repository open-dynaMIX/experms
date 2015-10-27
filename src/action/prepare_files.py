# -*- coding: utf-8 -*-

import sys
import os
import time
import re
from action import main as action


def is_excluded(path, excludepath, excluderegex):
    for excl in excludepath:
        if path.startswith(excl):
            return True

    if excluderegex:
        p = re.compile(excluderegex)
        if p.search(os.path.basename(path)):
            return True

    return False


def prepare(path, event, isdir, config, debug):
    """
    Prepare everything:
     - Check what rule has to be applied
     - Check if the file is excluded
    """
    if debug:
        if isdir:
            logpath = path + "/"
        else:
            logpath = path
        print >> sys.stderr, ("[debug] %s %s event to process: %s, %s"
                              % (time.strftime("%Y-%m-%d_%H:%M:%S",
                              time.localtime()), "%.20f" % time.time(),
                              event, logpath))

    ruledir = None
    dirhighest = 0
    for nr, item in enumerate(config.path):
        tempdirhighest = 0
        if not path.startswith(item):
            continue
        for count, thing in enumerate(path.split('/')):
            try:
                item.split('/')[count]
            except IndexError:
                break
            if thing == item.split('/')[count]:
                tempdirhighest = tempdirhighest + 1
        if tempdirhighest > dirhighest:
            if not is_excluded(path, config.excludepath[nr],
                               config.excluderegex[nr]):
                dirhighest = tempdirhighest
                ruledir = nr

    if not ruledir == None:
        action(path, event, isdir, config, ruledir, debug)

