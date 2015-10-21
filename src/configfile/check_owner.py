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
import pwd

def check_owner(parser, section, debug):
    if parser.has_option(section, 'owner'):
        tempowner = parser.get(section, 'owner')
        if tempowner == '':
            owner = None
        else:
            try:
                tempowner = int(tempowner)
            except ValueError:
                try:
                    pwd.getpwnam(tempowner)
                except KeyError:
                    print >> sys.stderr, ("Error in section %s: User %s "
                                          "doesn't exist." % (section,
                                          tempowner))
                    owner = False
                else:
                    # save the user as uid
                    owner = pwd.getpwnam(tempowner).pw_uid
                    if debug == True:
                        print >> sys.stderr, ("[debug] 'user' in section '%s' "
                                              "is valid" % section)
            else:
                try:
                    pwd.getpwuid(tempowner)
                except KeyError:
                    print >> sys.stderr, ("Error in section %s: User %s "
                                          "doesn't exist." % (section,
                                           tempowner))
                    owner = False
                else:
                    owner = tempowner
                    if debug == True:
                        print "'user' in section '" + section + "' is valid"
    else:
        owner = None

    return owner
