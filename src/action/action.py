# -*- coding: utf-8 -*-

import sys
import os
import time
from chown import chown
from chmodsym import chmod


def get_actperms(path):
    try:
        # use os.lstat instead of os.stat in order to not following symlinks
        actpermsraw = os.lstat(path)
    except OSError, e:
        if e.errno == 2:
            # this means the file/directory doesn't exist anymore
            return
    actperms = ([actpermsraw.st_uid, actpermsraw.st_gid,
                 actpermsraw.st_mode])
    return actperms


def main(path, event, isdir, config, ruledir, debug):
    actperms = get_actperms(path)

    somethinghappened = False

    if chown(path, actperms, config, ruledir):
        somethinghappened = True
        if debug:
            print >> sys.stderr, ("[debug] Section '%s': changed owner of "
                                  "'%s'" % (config.section[ruledir], path))

    if isdir:
        chmodmode = config.chmodd[ruledir]
    else:
        chmodmode = config.chmodf[ruledir]
    if chmod(path, actperms, chmodmode):
        somethinghappened = True
        if debug:
            print >> sys.stderr, ("[debug] Section '%s': changed permissions "
                                  "of '%s'" % (config.section[ruledir], path))


    if somethinghappened:
        if config.logit:
            if isdir:
                path = path + "/"
            print ("%s Section: %s Event: %s %s"
                   % (time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime()),
                   config.section[ruledir], event, path))
