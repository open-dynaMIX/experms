# -*- coding: utf-8 -*-


import sys
import os

def check_path(parser, section, debug):
    if parser.has_option(section, 'path'):
        dirname = parser.get(section, 'path').rstrip('/')
        if dirname == '':
            print >> sys.stderr, ("Error in section '%s': 'dirname' is not set."
                                  % section)
            path = None
        else:
            if not os.path.isdir(os.path.expanduser(dirname)):
                path = None
                print >> sys.stderr, ("Error in section '%s': 'path' '%s/' "
                                      "doesn't exist" % (section, dirname))
            else:
                path = os.path.expanduser(dirname)
                if debug:
                    print >> sys.stderr, ("[debug] 'path' in section '%s' "
                                          "is valid" % section)
    else:
        print >> sys.stderr, ("Error in section '%s': 'dirname' is not set."
                              % section)
        path = None

    return path

