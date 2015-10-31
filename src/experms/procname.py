# -*- coding: utf-8 -*-

from ctypes import cdll, byref, create_string_buffer


def set_procname(newname):
    """
    Change the name of the process to 'experms'.
    From blog.abhijeetr.com/2010/10/changing-process-name-of-python-script.html
    """
    libc = cdll.LoadLibrary('libc.so.6')        # Loading a 3rd party library C
    buff = create_string_buffer(len(newname)+1) # Note: One larger than the
                                                # name (man prctl says that)
    buff.value = newname                        # Null terminated string as it
                                                # should be
    libc.prctl(15, byref(buff), 0, 0, 0)        # Refer to "#define" of
                                                # "/usr/include/linux/prctl.h"
                                                # for the misterious value 16 &
                                                # arg[3..5] are zero as the man
                                                # page says.
