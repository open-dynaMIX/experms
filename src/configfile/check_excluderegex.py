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
                                      "'excludepattern' must be a regular "
                                      "expression." % section)
                excluderegex = False
            else:
                excluderegex = tempexcluderegex
                if debug:
                    print >> sys.stderr, ("[debug] 'excluderegex' in "
                                          "section '%s' is valid." % section)
    else:
        excluderegex = None

    if excluderegex in [None, '']:
        if debug:
            print >> sys.stderr, ("[debug] 'excluderegex' in section '%s' "
                                  "is not set." % section)

    return excluderegex
