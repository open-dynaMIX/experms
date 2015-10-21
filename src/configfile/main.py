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


# bold: "\033[1m"
# green: "\033[32;1m"
# red: "\033[31;1m"
# normal: "\033[0m"

import sys
import os
import ConfigParser
from configfile.check_printlog import check_printlog
from configfile.check_restore import check_restore
from configfile.check_path import check_path
from configfile.check_ownerandgroup import check_ownerandgroup
#from pwd import getpwnam, getpwuid
#from grp import getgrnam, getgrgid
#from re import compile as re_compile


class Check(object):
    """
    Read the configfile and set the values:
    self.restore = boolean
    self.logit = boolean
    self.sectionname = ['section1','section2','section3']
    self.dirname = ['dir1','dir2','dir3']
    self.owner = ['own1','own2','own3']
    self.group = ['grp1','grp2','grp3']
    self.chmodf = ['oct1','oct2','oct3']
    self.chmodd = ['oct1','oct2','oct3']
    self.excludedir = ['excludedir1','excludedir2','excludedir3']
    self.excludepattern = ['regex1','regex2','regex3']
    """
    def __init__(self, debug):

        self.debug = debug

        # default values for the section general
        self.logitdefault = False
        self.restoredefault = False

        # create the needed lists
        self.sectionname = []
        self.path = []
        self.owner = []
        self.group = []
        self.chmodf = []
        self.chmodd = []
        self.excludedir = []
        self.excludepattern = []

        #prepare the error variable
        self.errorsoccured = False

        # check for the existence of a config-file
        if os.path.isfile('/etc/experms.conf'):
            self.configfile = '/etc/experms.conf'
        elif os.path.isfile(sys.path[0] + '/experms.conf'):
            self.configfile = sys.path[0] + '/experms.conf'
        elif os.path.isfile(sys.path[0] + '/experms.conf'):
            self.configfile = sys.path[0] + '/experms.conf'
        else:
            print >> sys.stderr, ("\033[31;1mError: No configuration-file "
                                  "(/etc/experms.conf) was found.\033[0m")
            sys.exit(1)
        if debug:
            print >> sys.stderr, ("[debug] Using configuration-file '%s'"
                                  % (self.configfile))

        self.parser = self.parse_file()
        self.use_checks()

    def parse_file(self):
        parser = ConfigParser.SafeConfigParser()
        try:
            parser.read(self.configfile)
        except ConfigParser.MissingSectionHeaderError:
            pass
        return parser

    def use_checks(self):
        if self.parser.has_section('general'):
            self.logit = check_printlog(self.parser, self.logitdefault,
                                        self.debug)
            if self.logit == None:
                self.errorsoccured = True

            self.restore = check_restore(self.parser, self.restoredefault,
                                         self.debug)
            if self.restore == None:
                self.errorsoccured = True
        else:
            self.restore = self.restoredefault
            self.logit = self.logitdefault


        sectionfound = False
        for section in self.parser.sections():
            if section == 'general':
                continue
            sectionfound = True

            self.sectionname.append(section)

            temppath = check_path(self.parser, section, self.debug)
            if not temppath:
                self.errorsoccured = True
            else:
                self.path.append(temppath)

            tempowner = check_ownerandgroup(self.parser, section, 'owner', self.debug)
            if tempowner == False:
                self.errorsoccured = True
            else:
                self.owner.append(tempowner)

            tempgroup = check_ownerandgroup(self.parser, section, 'group', self.debug)
            if tempgroup == False:
                self.errorsoccured = True
            else:
                self.group.append(tempgroup)

        if not sectionfound:
            print >> sys.stderr, ("Error: No directory-section "
                                  "was found.\nIf you have started experms"
                                  " for the first time, please edit the "
                                  "configfile first (usually "
                                  "/etc/experms.conf)")
            self.errorsoccured = True

        if self.errorsoccured:
            print >> sys.stderr, ("Aborting!")
            sys.exit(1)

