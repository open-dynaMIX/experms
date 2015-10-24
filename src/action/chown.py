# -*- coding: utf-8 -*-

import os


def chown(path, actperms, config, ruledir):
    if config.owner[ruledir] in [actperms[0], None]:
        newowner = -1
    else:
        newowner = config.owner[ruledir]

    if config.group[ruledir] in [actperms[1], None]:
        newgroup = -1
    else:
        newgroup = config.group[ruledir]

    if not (newowner, newgroup) == (-1, -1):
        try:
            os.lchown(path, newowner, newgroup)
        except OSError, e:
            if e.errno == 2:
                # this means the file/directory doesn't exist anymore
                return False
        else:
            return True

    return False
