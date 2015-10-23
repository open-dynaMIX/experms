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
import grp

def check_ownerandgroup(parser, section, oorg, debug):
    if oorg == 'owner':
        switch = "User"
    else:
        switch = "Group"

    if not parser.has_option(section, oorg):
        owner = None
        if debug:
            print >> sys.stderr, ("[debug] '%s' in section '%s' is not set."
                                  % (oorg, section))
    else:
        tempowner = parser.get(section, oorg)
        if tempowner == '':
            owner = None
        else:
            try:
                tempowner = int(tempowner)
            except ValueError:
                try:
                    if oorg == 'owner':
                        pwd.getpwnam(tempowner)
                    else:
                        grp.getgrnam(tempowner)
                except KeyError:
                    owner = False
                    print >> sys.stderr, ("Error in section '%s': %s '%s' "
                                          "doesn't exist." % (section, switch,
                                          tempowner))
                else:
                    # save the user/group as uid
                    if oorg == 'owner':
                        owner = pwd.getpwnam(tempowner).pw_uid
                    else:
                        owner = grp.getgrnam(tempowner).gr_gid
                    if debug:
                        print >> sys.stderr, ("[debug] '%s' in section '%s' "
                                              "is valid" % (oorg, section))
            else:
                try:
                    if oorg == 'owner':
                        pwd.getpwuid(tempowner)
                    else:
                        grp.getgrgid(tempowner)
                except KeyError:
                    print >> sys.stderr, ("Error in section '%s': %s '%s' "
                                          "doesn't exist." % (section, switch,
                                          tempowner))
                    owner = False
                else:
                    owner = tempowner
                    if debug:
                        print >> sys.stderr, ("[debug] '%s' in section '%s' "
                                              "is valid" % (oorg, section))

    return owner
