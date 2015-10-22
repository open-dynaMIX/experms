# -*- coding: utf-8 -*-

"""  module chmodsym.py (linux)

This module defines a function chmod(location, description)
which allows to change a file's permission with a symbolic
description of the mode, similar to the shell command 'chmod'.

Tested with python 2.6 and 3.1.
"""

import os, stat
import functools
import operator
import re

def isint(description):
    try:
        int(description)
    except ValueError:
        return False
    else:
        return True

def verify_chmod(description):
    if isint(description):
        try:
            int(description, 8)
        except ValueError:
            return False
        else:
            if len(description) < 3 or len(description) > 4:
                return False
            else:
                return True
    else:
        p = re.compile(r"^([ugo]*|[a]?)([+\-=])([ugo]|[rwx]*)$")
        if p.match(description):
            return True
        else:
            return False


def chmod(location, description):
    """chmod(location, description) --> None
    Change the access permissions of file, using a symbolic description
    of the mode, similar to the format of the shell command chmod.
    The format of description is
        * a sequence of letters in o, g, u or one letter a (no letter means a)
        * an operator in +, -, =
        * a sequence of letters in r, w, x, or a single letter in o, g, u
    Example:
        chmod(myfile, "ug+w")   # make the file writable for the owner and the
                                # group
        chmod(myfile, "u+x")    # make the file executable for it's owner.
        chmod(myfile, "o-rwx")  # remove all permissions for all users not in
                                # the group.
    See also the man page of chmod.
    """
    if chmod.regex is None:
        chmod.regex = re.compile(r"^(?P<who>[ugo]*|[a]?)(?P<op>[+\-=])"
                                  "(?P<value>[ugo]|[rwx]*)$")
    mo = chmod.regex.match(description)
    who, op, value = mo.group("who"), mo.group("op"), mo.group("value")
    if not who:
        who = "a"
    for person in who:
        mode = os.stat(location)[stat.ST_MODE]
        if value in ("o", "g", "u"):
            mask = ors((stat_bit(person, z) for z in "rwx" if (mode & stat_bit(value, z))))
        else:
            mask = ors((stat_bit(person, z) for z in value))
        if op == "=":
            mode &= ~ ors((stat_bit(person, z) for z in  "rwx"))
        mode = (mode & ~mask) if (op == "-") else (mode | mask)
        os.chmod(location, mode)

chmod.regex = None

# Helper functions

def stat_bit(who, letter):
    if who == "a":
        return stat_bit("o", letter) | stat_bit("g", letter) | stat_bit("u", letter)
    return getattr(stat, "S_I%s%s" % (letter.upper(), stat_bit.prefix[who]))

stat_bit.prefix = dict(u = "USR", g = "GRP", o = "OTH")

def ors(sequence, initial = 0):
    return functools.reduce(operator.__or__, sequence, initial)

# Test code

def test_code():

    import subprocess as sp

    def touch(location):
       sp.Popen("touch %s" % location, shell=True).wait()

    def get_mode_by_ls(location):
       """Run ls and return a string like '-r--r--r-' giving the mode."""
       popen = sp.Popen(["ls", "-l", location], stdout=sp.PIPE)
       sout, serr = popen.communicate()
       return sout[:10]

    loc = "/home/fabio/Desktop/testfile.py"
    touch(loc)
    print(get_mode_by_ls(loc))
    for desc in ("g+rx", "a=g", "o-rw", "u=o", "+rwx", "a-wx", "u+s"):
       chmod(loc, desc)
       print("%s --> %s" % (desc, get_mode_by_ls(loc)))

if __name__ == "__main__":
    #test_code()
    verify_chmod('a+g')
