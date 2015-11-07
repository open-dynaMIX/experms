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
                if not item.startswith(path):
                    print >> sys.stderr, ("Error in section '%s': "
                                          "'excludepath' must be inside 'path'"
                                          % section)
                    excludepath = False
                else:
                    if not excludepath == False:
                        excludepath.append(item)
                    if debug:
                        print >> sys.stderr, ("[debug] 'excludepath' '%s' in "
                                              "section '%s' is valid"
                                              % (item, section))

        if path in excludepath:
            excludepath = False
            print >> sys.stderr, ("Error in section '%s': 'path' is in "
                                  "'excludepath'" % (section))
    else:
        excludepath = None
        if debug:
            print >> sys.stderr, ("[debug] 'excludepath' in section '%s' "
                                  "is not set" % section)

    if excludepath == []:
        excludepath = None
        if debug:
            print >> sys.stderr, ("[debug] 'excludepath' in section '%s' "
                                  "is not set" % section)

    return excludepath


