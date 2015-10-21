# -*- coding: utf-8 -*-

"""
Copyright (C) 2015, Fabio Rämi
All rights reserved.

GNU GPL v3.0 or later.
http://www.gnu.org/licenses/gpl-3.0.txt
Experms comes with absolutely no warranty!

Experms is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Experms is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Experms.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys

def check_printlog(parser, logitdefault, debug):
    if parser.has_option('general', 'log_activities'):
        logit = parser.get('general', 'log_activities').lower()
        if logit == 'yes':
            logit = True
            if debug == True:
                print >> sys.stderr, ("[debug] experms will print a log")
        elif logit == 'no':
            logit = False
            if debug == True:
                print >> sys.stderr, ("[debug] experms won't print a log")
        else:
            print >> sys.stderr, ("Error: 'log_activities' "
                                  "must be either 'yes' or 'no'")
            logit = None
    else:
        logit = logitdefault
        if debug == True:
            print >> sys.stderr, ("[debug] experms won't print a log")
    return logit
