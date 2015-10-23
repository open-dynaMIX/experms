# -*- coding: utf-8 -*-

"""  module chmodsym.py (linux)

This module defines a function chmod(path, description)
which allows to change a file's permission with a symbolic
description of the mode, similar to the shell command 'chmod'.

Tested with python 2.6 and 3.1.
"""

import os, stat
import functools
import operator
import re


def chmod(path, actperms, description):
    """chmod(path, description) --> None
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

    if not description:
        return False

    if isint(description):
        if handle_octal(path, actperms, description):
            return True
        else:
            return False
    else:
        if handle_symbolic(path, actperms, description):
            return True
        else:
            return False

chmod.regex = None



def handle_octal(path, actperms, description):
    if len(description) == 3:
        description = '0' + description
    if description == oct(actperms[2] & 0777):
        return False
    else:
        os.chmod(path, int(description, 8))
        return True

def handle_symbolic(path, actperms, description):
    if chmod.regex is None:
        chmod.regex = re.compile(r"^(?P<who>[ugo]*|[a]?)(?P<op>[+\-=])"
                                  "(?P<value>[ugo]|[rwx]*)$")
        mo = chmod.regex.match(description)
        who, op, value = mo.group("who"), mo.group("op"), mo.group("value")
        if not who:
            who = "a"
        mode = actperms[2]
        modeold = mode
        for person in who:
            if value in ("o", "g", "u"):
                mask = (ors((stat_bit(person, z) for z in "rwx"
                        if (mode & stat_bit(value, z)))))
            else:
                mask = ors((stat_bit(person, z) for z in value))
            if op == "=":
                mode &= ~ ors((stat_bit(person, z) for z in  "rwx"))
            mode = (mode & ~mask) if (op == "-") else (mode | mask)

        if mode == modeold:
            return False
        else:
            os.chmod(path, mode)
            return True


# Helper functions

def stat_bit(who, letter):
    if who == "a":
        return stat_bit("o", letter) | stat_bit("g", letter) | stat_bit("u", letter)
    return getattr(stat, "S_I%s%s" % (letter.upper(), stat_bit.prefix[who]))

stat_bit.prefix = dict(u = "USR", g = "GRP", o = "OTH")


def ors(sequence, initial = 0):
    return functools.reduce(operator.__or__, sequence, initial)


def isint(description):
    try:
        int(description)
    except ValueError:
        return False
    else:
        return True


# Test code

def test_code():

    import subprocess as sp

    def touch(path):
       sp.Popen("touch %s" % path, shell=True).wait()

    def get_mode_by_ls(path):
       """Run ls and return a string like '-r--r--r-' giving the mode."""
       popen = sp.Popen(["ls", "-l", path], stdout=sp.PIPE)
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
