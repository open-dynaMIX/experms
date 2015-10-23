# -*- coding: utf-8 -*-


import sys
import re


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


def verify_chmod(description):
    if isint(description):
        try:
            int(description, 8)
        except ValueError:
            return False
        else:
            if len(description) < 3 or len(description) > 4:
                return False
            else:
                return True
    else:
        p = re.compile(r"^([ugo]*|[a]?)([+\-=])([ugo]|[rwx]*)$")
        if p.match(description):
            return True
        else:
            return False


def isint(description):
    try:
        int(description)
    except ValueError:
        return False
    else:
        return True
