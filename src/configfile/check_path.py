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

def check_path(parser, section, debug):
    if parser.has_option(section, 'path'):
        dirname = parser.get(section, 'path').rstrip('/')
        if dirname == '':
            print >> sys.stderr, ("Error in section " + section
                                  + ": 'path' is empty.\nIf you have "
                                  "started experms for the first time,"
                                  " please edit the configfile first.")
            path = None
        else:
            if not os.path.isdir(os.path.expanduser(dirname)):
                path = None
                print >> sys.stderr, ("Error in section " + section +
                                      ": 'path' " + dirname + "/ doesn't exist")
            else:
                path = os.path.expanduser(dirname)
                if debug == True:
                    print >> sys.stderr, ("[debug] 'path' in section '" + section +
                                          "' is valid")
    else:
        print >> sys.stderr, ("Error in section " + section +
                              ": 'dirname' is not set.")
        path = None

    return path

