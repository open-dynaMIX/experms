# -*- coding: utf-8 -*-


import sys

def check_restore(parser, restoredefault, debug):
    if parser.has_option('general', 'restore'):
        restore = parser.get('general', 'restore').lower()
        if restore == 'yes':
            restore = True
            if debug:
                print >> sys.stderr, ("[debug] experms will restore at "
                                      "startup")
        elif restore == 'no':
            restore = False
            if debug:
                print >> sys.stderr, ("[debug] experms won't restore at "
                                      "startup")
        else:
            print >> sys.stderr, ("Error: 'restore' must be "
                                  "either 'yes' or 'no'")
            restore = None
    else:
        restore = restoredefault
        if debug:
            print >> sys.stderr, ("[debug] experms won't restore at startup")

    return restore

