# -*- coding: utf-8 -*-


import sys
import re


def check_excluderegex(parser, section, debug):
    excluderegex = None

    if parser.has_option(section, 'excluderegex'):
        tempexcluderegex = parser.get(section, 'excluderegex')
        if tempexcluderegex == '':
            excluderegex = None
        else:
            try:
                re.compile(tempexcluderegex)
            except:
                print >> sys.stderr, ("Error in section '%s': "
                                      "'excluderegex' must be a regular "
                                      "expression" % section)
                excluderegex = False
            else:
                excluderegex = tempexcluderegex
                if debug:
                    print >> sys.stderr, ("[debug] 'excluderegex' in "
                                          "section '%s' is valid" % section)
    else:
        excluderegex = None

    if excluderegex in [None, '']:
        if debug:
            print >> sys.stderr, ("[debug] 'excluderegex' in section '%s' "
                                  "is not set" % section)

    return excluderegex
