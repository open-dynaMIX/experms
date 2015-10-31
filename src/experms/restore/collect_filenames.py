#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import re

def collect(config):
    """
    collects all the filenames in the monitored directories
    returns an array: [[dirnames],[filenames]]
    """
    realpaths = []
    for item in config.path:
        doappend = True
        for thing in config.path:
            if not item == thing:
                p = re.compile('^' + thing + '/')
                if p.search(item):
                    doappend = False
                    break
        if doappend == True:
            realpaths.append(item)

    matchesfile = []
    matchesdir = []
    for item in realpaths:
        for root, dirnames, filenames in os.walk(item):
            for filename in filenames:
                filenamewrite = os.path.join(root, filename)
                matchesfile.append(filenamewrite)
            for dirname in dirnames:
                dirnamewrite = os.path.join(root, dirname)
                matchesdir.append(dirnamewrite)
    # Add the watched dirs to the lists
    for thing in realpaths:
        matchesdir.append(thing)

    return [matchesdir, matchesfile]
