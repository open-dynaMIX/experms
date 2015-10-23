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
import os


def check_excludepath(parser, section, path, debug):
    excludepath = []
    if parser.has_option(section, 'excludepath'):
        tempexcludepath = parser.get(section, 'excludepath').split(',')
        for item in tempexcludepath:
            item = os.path.expanduser(item).strip().rstrip('/')
            if item == '':
                continue
            else:
                if not os.path.isdir(item) and not os.path.isfile(item):
                    print >> sys.stderr, ("Error in section '%s': "
                                          "'excludepath' %s doesn't exist."
                                          % (section, item))
                    excludepath.append(False)
                else:
                    excludepath.append(item)
                    if debug:
                        print >> sys.stderr, ("[debug] Excludedir '%s' in "
                                              "section '%s' is valid."
                                              % (item, section))

        if path in excludepath:
            excludepath = [False]
            print >> sys.stderr, ("Error in section '%s': 'path' is in "
                                  "'excludepath'." % (section))

    if debug:
        if excludepath == []:
            print >> sys.stderr, ("[debug] 'excludepath' in section '%s' "
                                  "is not set." % section)

    return excludepath


