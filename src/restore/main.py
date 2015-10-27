#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from collect_filenames import collect
from action.prepare_files import prepare


def restore(config, debug):
    """
    Restores all the ownerships and permissions on all files
    """
    filenames = collect(config)
    for item in filenames[0]:
        prepare(item, 'RESTORE', True, config, debug)
    for item in filenames[1]:
        prepare(item, 'RESTORE', False, config, debug)
