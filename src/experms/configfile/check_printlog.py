# -*- coding: utf-8 -*-


import sys

def check_printlog(parser, logitdefault, debug):
    if parser.has_option('general', 'log_activities'):
        logit = parser.get('general', 'log_activities').lower()
        if logit == 'yes':
            logit = True
            if debug:
                print >> sys.stderr, ("[debug] experms will print a log")
        elif logit == 'no':
            logit = False
            if debug:
                print >> sys.stderr, ("[debug] experms won't print a log")
        elif logit == '':
            logit = logitdefault
            if debug:
                print >> sys.stderr, ("[debug] 'log_activities' defaults to "
                                      "%s" % logitdefault)
        else:
            print >> sys.stderr, ("Error: 'log_activities' "
                                  "must be either 'yes' or 'no'")
            logit = None
    else:
        logit = logitdefault
        if debug:
            print >> sys.stderr, ("[debug] experms won't print a log")
    return logit
