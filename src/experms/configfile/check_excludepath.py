# -*- coding: utf-8 -*-


import sys
import os


def check_excludepath(parser, section, path, debug):
    excludepath = []
    if parser.has_option(section, 'excludepath'):
        tempexcludepath = parser.get(section, 'excludepath').split(',')
        for item in tempexcludepath:
            item = os.path.expanduser(item).strip().rstrip('/')
            if item in ['', 'None', 'none']:
                continue
            else:
                if item.startswith(path) and not item == path:
                    if not excludepath == False:
                        excludepath.append(item)
                    if debug:
                        print >> sys.stderr, ("[debug] 'excludepath' '%s' in "
                                              "section '%s' is valid"
                                              % (item, section))
                elif item == path:
                    excludepath = False
                    print >> sys.stderr, ("Error in section '%s': "
                                          "'excludepath' cannot be the same "
                                          "as 'path'" % section)
                else:
                    excludepath = False
                    print >> sys.stderr, ("Error in section '%s': "
                                          "'excludepath' must be inside "
                                          "'path'" % section)
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
