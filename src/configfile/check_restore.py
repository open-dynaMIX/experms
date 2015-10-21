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

def check_restore(parser, restoredefault, debug):
    if parser.has_option('general', 'restore'):
        restore = parser.get('general', 'restore').lower()
        if restore == 'yes':
            restore = True
            if debug == True:
                print >> sys.stderr, ("[debug] experms will restore at "
                                      "startup")
        elif restore == 'no':
            restore = False
            if debug == True:
                print >> sys.stderr, ("[debug] experms won't restore at "
                                      "startup")
        else:
            print >> sys.stderr, ("Error: 'restore' must be "
                                  "either 'yes' or 'no'")
            restore = None
    else:
        restore = restoredefault
        if debug == True:
            print >> sys.stderr, ("[debug] experms won't restore at startup")

    return restore

