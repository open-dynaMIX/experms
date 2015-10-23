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
import ConfigParser
from configfile.check_printlog import check_printlog
from configfile.check_restore import check_restore
from configfile.check_path import check_path
from configfile.check_ownerandgroup import check_ownerandgroup
from configfile.check_chmod import check_chmod
from configfile.check_excludepath import check_excludepath
from configfile.check_excluderegex import check_excluderegex


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
    self.excludepath = ['excludepath1','excludepath2','excludepath3']
    self.excluderegex = ['regex1','regex2','regex3']
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
        self.excludepath = []
        self.excluderegex = []

        self.errorsoccured = False

        configfile = self.find_configfile()

        parser = self.parse_configfile(configfile)

        self.call_checks(parser)


    def find_configfile(self):
        if os.path.isfile('/etc/experms.conf'):
            configfile = '/etc/experms.conf'
        elif os.path.isfile(sys.path[0] + '/experms.conf'):
            configfile = sys.path[0] + '/experms.conf'
        else:
            print >> sys.stderr, ("\033[31;1mError: No configuration-file "
                                  "(/etc/experms.conf) was found.\033[0m")
            sys.exit(1)
        if self.debug:
            print >> sys.stderr, ("[debug] Using configuration-file '%s'"
                                  % (configfile))
        return configfile


    def parse_configfile(self, configfile):
        parser = ConfigParser.SafeConfigParser()
        try:
            parser.read(configfile)
        except ConfigParser.MissingSectionHeaderError:
            pass
        return parser


    def call_checks(self, parser):
        self.check_general(parser)

        if not self.check_sections(parser):
            print >> sys.stderr, ("Error: No directory-section "
                                  "was found.\nIf you have started experms"
                                  " for the first time, please edit the "
                                  "configfile first (usually "
                                  "/etc/experms.conf)")
            self.errorsoccured = True

        if self.errorsoccured:
            print >> sys.stderr, ("Aborting!")
            sys.exit(1)


    def check_general(self, parser):
        if parser.has_section('general'):
            self.logit = check_printlog(parser, self.logitdefault,
                                        self.debug)
            if self.logit == None:
                self.errorsoccured = True

            self.restore = check_restore(parser, self.restoredefault,
                                         self.debug)
            if self.restore == None:
                self.errorsoccured = True
        else:
            self.restore = self.restoredefault
            self.logit = self.logitdefault


    def check_sections(self, parser):
        sectionfound = False
        for section in parser.sections():
            if section == 'general':
                continue
            sectionfound = True

            self.sectionname.append(section)

            temppath = check_path(parser, section, self.debug)
            if not temppath:
                self.errorsoccured = True
            else:
                self.path.append(temppath)

            tempowner = check_ownerandgroup(parser, section, 'owner',
                                            self.debug)
            if tempowner == False:
                self.errorsoccured = True
            else:
                self.owner.append(tempowner)

            tempgroup = check_ownerandgroup(parser, section, 'group',
                                            self.debug)
            if tempgroup == False:
                self.errorsoccured = True
            else:
                self.group.append(tempgroup)

            tempchmodf = check_chmod(parser, section, 'chmodf', self.debug)
            if tempgroup == False:
                self.errorsoccured = True
            else:
                self.chmodf.append(tempchmodf)

            tempchmodd = check_chmod(parser, section, 'chmodd', self.debug)
            if tempgroup == False:
                self.errorsoccured = True
            else:
                self.chmodd.append(tempchmodd)

            tempexcludepath = check_excludepath(parser, section,
                                                self.path[-1], self.debug)
            excludepatherror = False
            for location in tempexcludepath:
                if not location:
                    excludepatherror = True
            if excludepatherror:
                self.errorsoccured = True
            else:
                self.excludepath.append(tempexcludepath)


            tempexcluderegex = check_excluderegex(parser, section, self.debug)
            if tempexcluderegex == False:
                self.errorsoccured = True
            else:
                self.excluderegex.append(tempexcluderegex)


        return sectionfound
