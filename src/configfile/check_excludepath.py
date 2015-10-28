# -*- coding: utf-8 -*-


import sys
import os


def check_excludepath(parser, section, path, debug):
    excludepath = []
    if parser.has_option(section, 'excludepath'):
        tempexcludepath = parser.get(section, 'excludepath').split(',')
        for item in tempexcludepath:
            item = os.path.expanduser(item).strip().rstrip('/')
            if item == '':
                continue
            else:
                if not os.path.isdir(item) and not os.path.isfile(item):
                    print >> sys.stderr, ("Error in section '%s': "
                                          "'excludepath' '%s' doesn't exist"
                                          % (section, item))
                    excludepath.append(False)
                else:
                    excludepath.append(item)
                    if debug:
                        print >> sys.stderr, ("[debug] Excludedir '%s' in "
                                              "section '%s' is valid"
                                              % (item, section))

        if path in excludepath:
            excludepath = [False]
            print >> sys.stderr, ("Error in section '%s': 'path' is in "
                                  "'excludepath'" % (section))

    if debug:
        if excludepath == []:
            print >> sys.stderr, ("[debug] 'excludepath' in section '%s' "
                                  "is not set" % section)

    return excludepath


