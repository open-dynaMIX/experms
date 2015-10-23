# -*- coding: utf-8 -*-

import sys
import os
import time
import re



def prepare(path, event, isdir, config, debug):
    """
    Prepare everything:
     - Check what rule has to be applied
     - Check if the file is excluded
    """
    if debug:
        print >> sys.stderr, ("[debug] %s %s event to process: %s, %s"
                              % (time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()),
                              "%.20f" % time.time(), event, path))


    dirhighest = 0
    for nr, item in enumerate(config.path):
        tempdirhighest = 0
        if not item in path:
            continue
        for count, thing in enumerate(path.split('/')):
            try:
                item.split('/')[count]
            except IndexError:
                break
            if thing == item.split('/')[count]:
                tempdirhighest = tempdirhighest + 1
        if tempdirhighest > dirhighest:
            dirhighest = tempdirhighest
            ruledir = nr

    # check if the file is excluded or what rules have to take effect
    if not config.excluderegex[ruledir] == None:
        if not isdir:
            p = re.compile(config.excluderegex[ruledir])
            if p.search(os.path.basename(path)):
                return
    if config.excludepath[ruledir] == None:
        highest = 0
    else:
        highest = 0
        for item in config.excludepath[ruledir]:
            if not item in path:
                continue
            temphighest = 0
            for ruledir, thing in enumerate(path.split('/')):
                try:
                    item.split('/')[ruledir]
                except IndexError:
                    break
                if thing == item.split('/')[ruledir]:
                    temphighest = temphighest + 1
            if temphighest > highest:
                highest = temphighest

    if highest > dirhighest:
        return

    print path, event, ruledir

    # action(directory, event, ruledir, restore)

