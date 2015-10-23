# -*- coding: utf-8 -*-


import sys
from action.chmodsym import verify_chmod

def check_chmod(parser, section, what, debug):
    if parser.has_option(section, what):
        tempchmod = parser.get(section, what)
        if verify_chmod(tempchmod):
            chmod = tempchmod
            if debug:
                print >> sys.stderr, ("[debug] '%s' in section '%s' "
                                      "is valid" % (what, section))
        else:
            chmod = False
            print >> sys.stderr, ("Error in section '%s': '%s' is not a valid "
                                  "setting." % (section, what))
    else:
        chmod = None
        if debug:
            print >> sys.stderr, ("[debug] '%s' in section '%s' not set."
                                  % (what, section))

    return chmod


