# -*- coding: utf-8 -*-


import sys
import pwd
import grp

def check_ownerandgroup(parser, section, oorg, debug):
    if oorg == 'owner':
        switch = "User"
    else:
        switch = "Group"

    if not parser.has_option(section, oorg):
        if debug:
            print >> sys.stderr, ("[debug] '%s' in section '%s' is not set"
                                  % (oorg, section))
        return None

    tempowner = parser.get(section, oorg)
    if tempowner in ['', 'None', 'none']:
        if debug:
            print >> sys.stderr, ("[debug] '%s' in section '%s' is not "
                                  "set" % (oorg, section))
        return None

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
                                  "doesn't exist" % (section, switch,
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
                                  "doesn't exist" % (section, switch,
                                  tempowner))
            owner = False
        else:
            owner = tempowner
            if debug:
                print >> sys.stderr, ("[debug] '%s' in section '%s' "
                                      "is valid" % (oorg, section))

    return owner
