# -*- coding: utf-8 -*-

import os


def chown(path, oldowner, newowner, debug):
    if not oldowner == newowner:
        os.lchown(path, newowner, -1)
        return True

    return False
