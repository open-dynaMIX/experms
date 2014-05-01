#!/usr/bin/env python2
# -*- coding: utf-8 -*-

##
##         //\  //\  //\  //\  //\  //\  //\
##        //  \//  \//  \//  \//  \//  \//  \
##       //    _   _   _   _   _   _   _     \
##      //    / \ / \ / \ / \ / \ / \ / \     \
##     //    ( E ) X ) P ) E ) R ) M ) S )     \
##    //  __  \_/ \_/ \_/ \_/ \_/ \_/ \_/   __  \
##   // //  \                             //  \  \
##  // //    \  //\  //\  //\  //\  //\  //    \  \
##  \_//      \//  \//  \//  \//  \//  \//      \_//
##
##                 version 0.8 - 2013
##


##===========================================================================================================================
##
##         FILE: check-config.py
##
##  DESCRIPTION: Parses the configuration file, check validity and store content to variables
##
##       AUTHOR: Fabio Rämi - fabio(a)dynamix-tontechnik.ch
##
##      VERSION: 0.8
##
##      LICENCE: GNU GPL v3.0 or later.
##               http://www.gnu.org/licenses/gpl-3.0.txt
##               Experms comes with absolutely no warranty!
##               
##      COPYING: This file is part of Experms.
##
##               Experms is free software: you can redistribute it and/or modify
##               it under the terms of the GNU General Public License as published by
##               the Free Software Foundation, either version 3 of the License, or
##               (at your option) any later version.
##           
##               Experms is distributed in the hope that it will be useful,
##               but WITHOUT ANY WARRANTY; without even the implied warranty of
##               MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##               GNU General Public License for more details.
##           
##               You should have received a copy of the GNU General Public License
##               along with Experms.  If not, see <http://www.gnu.org/licenses/>.
##
##      CREATED: 2013
##               2014
##
##===========================================================================================================================

# bold: "\033[1m"
# green: "\033[32;1m"
# red: "\033[31;1m"
# normal: "\033[0m"

import sys
from os import path as os_path
from pwd import getpwnam, getpwuid
from grp import getgrnam, getgrgid
from re import compile as re_compile
from ConfigParser import SafeConfigParser,MissingSectionHeaderError


# function to verify the given octal permissions
def checkoctalperms(octalperms, chmodfd, i, debug):
  if chmodfd == 'chmodf':
    anrede = 'chmodf'
  else:
    anrede = 'chmodd'
  if octalperms != ['']:
    try:
      int(octalperms)
    except ValueError:
      print >> sys.stderr, "\033[31;1mError in section", i + ":", anrede, "is not an interger.\033[0m"
      return False
    if len(octalperms) != 3 and len(octalperms) != 4:
      print >> sys.stderr, "\033[31;1mError in section", i + ":", anrede, "needs to be a three or four digit octal number.\033[0m"
      return False
    for thing in octalperms:
      if int(thing) > 7:
        print >> sys.stderr, "\033[31;1mError in section", i + ":", anrede, "is not an octal number.\033[0m"
        return False
    if debug == True:
      print "'" + anrede + "' in section '" + i + "' is valid"
    return True

class Check(object):
  """
  Read the configfile and return the values:
  restore = boolean
  logit = boolean
  sectionname = ['section1','section2','section3']
  dirname = ['dir1','dir2','dir3']
  owner = ['own1','own2','own3']
  group = ['grp1','grp2','grp3']
  chmodf = ['oct1','oct2','oct3']
  chmodd = ['oct1','oct2','oct3']
  excludedir = ['excludedir1','excludedir2','excludedir3']
  excludepattern = ['regex1','regex2','regex3']
  doit = ['oct1','oct2','oct3']
  The list 'doit' contains octal value:
  1 = chown
  2 = chmodf
  4 = chmodd
  """
  def __init__(self, uid, debug):
    # variable names from the configfile
    log_activities = 'log_activities'
    restore = 'restore'
    dirname = 'path'
    owner = 'owner'
    group = 'group'
    chmodf = 'chmodf'
    chmodd = 'chmodd'
    excludedir = 'excludepath'
    excludepattern = 'excludepattern'
    
    # default values for the section general
    logitdefault = 'no'
    restoredefault = 'no'
    
    # create the needed lists
    self.doit = []
    self.dirname = []
    self.owner = []
    self.group = []
    self.chmodf = []
    self.chmodd = []
    self.excludedir = []
    self.excludepattern = []
    
    #prepare the error variable
    errorsoccured = False
    
    # check for the existence of a config-file
    if uid == 0:
      if os_path.isfile('/etc/experms.conf'):
        configfile = '/etc/experms.conf'
      elif os_path.isfile(sys.path[0] + '/experms.conf'):
        configfile = sys.path[0] + '/experms.conf'
      else:
        print >> sys.stderr, "\033[31;1mError: No configuration-file (/etc/experms.conf) was found.\033[0m"
        sys.exit(1)
    else:
      home = os_path.expanduser("~")
      if os_path.isfile(home + '/.experms.conf'):
        configfile = home + '/.experms.conf'
      elif os_path.isfile(home + '/experms.conf'):
        configfile = home + '/experms.conf'
      elif os_path.isfile(sys.path[0] + '/experms.conf'):
        configfile = sys.path[0] + '/experms.conf'
      else:
        print >> sys.stderr, "\033[31;1mError: No configuration-file (~/experms.conf or ~/.experms.conf) was found.\033[0m"
        sys.exit(1)
    print "Using configuration-file '" + configfile + "'"
    
    # parse the config-file
    parser = SafeConfigParser()
    try:
      parser.read(configfile)
    except MissingSectionHeaderError:
      pass

    if parser.has_section('general'):
      if debug == True:
        print "section 'general' was found"
      if parser.has_option('general', log_activities):
        self.logit = parser.get('general', log_activities).lower()
        if self.logit == 'yes':
          if debug == True:
            print 'experms will write a log'
        elif self.logit == 'no' or self.logit == '':
          self.logit = logitdefault
          if debug == True:
            print "experms won't write a log"
        else:
          print >> sys.stderr, "\033[31;1mError: 'log_activities' must be either 'yes' or 'no'\033[0m"
          errorsoccured = True
      else:
        self.logit = logitdefault
        if debug == True:
          print "experms won't write a log"
      
      if parser.has_option('general', restore):
        self.restore = parser.get('general', restore).lower()
        if self.restore == 'yes':
          if debug == True:
            print 'experms will restore at start'
        elif self.restore == 'no' or self.restore == '':
          self.restore = restoredefault
          if debug == True:
            print "experms won't restore at start"
        else:
          print >> sys.stderr, "\033[31;1mError: 'restore' must be either 'yes' or 'no'\033[0m"
          errorsoccured = True
      else:
        self.restore = restoredefault
        if debug == True:
          print "experms won't restore at start"
    
      if len(parser.sections()) < 2:
        print >> sys.stderr, "\033[31;1mError: No directory-section was found.\nIf you have started experms for the first time, please edit the configfile first (usually /etc/experms.conf)\033[0m"
        errorsoccured = True
    else:
      self.restore = restoredefault
      self.logit = logitdefault
      if len(parser.sections()) < 1:
        print >> sys.stderr, "\033[31;1mError: No directory-section was found.\nIf you have started experms for the first time, please edit the configfile first (usually /etc/experms.conf)\033[0m"
        errorsoccured = True
    


    self.sectionname = []
    # can't use enumerate here, to make it possible to mixup the order between general and directory sections in the config
    number = -1
    for i in parser.sections():
      if i == 'general':
        continue
      number = number + 1
      self.sectionname.append(i)
      usowchmoderr = True
      self.doit.append('')
      
      if parser.has_option(i, dirname):
        self.dirname.append('')
        self.dirname[number] = parser.get(i, dirname).rstrip('/')
        if self.dirname[number] == '':
          print >> sys.stderr, "\033[31;1mError in section", i + ": 'path' is empty.\nIf you have started experms for the first time, please edit the configfile first.\033[0m"
          errorsoccured = True
        else:
          if not os_path.isdir(self.dirname[number]):
            print >> sys.stderr, "\033[31;1mError in section", i + ": 'path'", self.dirname[number], "doesn't exist\033[0m"
            errorsoccured = True
          else:
            if debug == True:
              print "'dirname' in section '" + i + "' is valid"
      else:
        print >> sys.stderr, "\033[31;1mError in section", i + ": 'dirname' is not set.\033[0m"
        errorsoccured = True
      
      self.owner.append('')  
      if parser.has_option(i, owner):
        self.owner[number] = parser.get(i, owner)
        if self.owner[number] != '':
          try:
            self.owner[number] = int(self.owner[number])
          except ValueError:
            try:
              getpwnam(self.owner[number])
            except KeyError:
              print >> sys.stderr, "\033[31;1mError in section", i + ": User", self.owner[number], "doesn't exist.\033[0m"
              errorsoccured = True
            else:
              # save the user as uid
              self.owner[number] = getpwnam(self.owner[number]).pw_uid
              usowchmoderr = False
              self.doit[number] = 1
              if debug == True:
                print "'user' in section '" + i + "' is valid"
          else:
            try:
              getpwuid(self.owner[number])
            except KeyError:
              print >> sys.stderr, "\033[31;1mError in section", i + ": User", self.owner[number], "doesn't exist.\033[0m"
              errorsoccured = True
            else:
              usowchmoderr = False
              self.doit[number] = 1
              if debug == True:
                print "'user' in section '" + i + "' is valid"
            
        else:
          self.owner[number] = -1
          self.doit[number] = 0
      else:
        self.owner[number] = -1
        self.doit[number] = 0
      
      self.group.append('')
      if parser.has_option(i, group):
        self.group[number] = parser.get(i, group)
        if self.group[number] != '':
          try:
            self.group[number] = int(self.group[number])
          except ValueError:
            try:
              getgrnam(self.group[number])
            except KeyError:
              print >> sys.stderr, "\033[31;1mError in section", i + ": Group", self.group[number], "doesn't exist.\033[0m"
              errorsoccured = True
            else:
              # save the group as gid
              self.group[number] = getgrnam(self.group[number]).gr_gid
              usowchmoderr = False
              self.doit[number] = 1
              if debug == True:
                print "'group' in section '" + i + "' is valid"
          else:
            try:
              getgrgid(self.group[number])
            except KeyError:
              print >> sys.stderr, "\033[31;1mError in section", i + ": Group", self.group[number], "doesn't exist.\033[0m"
              errorsoccured = True
            else:
              usowchmoderr = False
              self.doit[number] = 1
              if debug == True:
                print "'group' in section '" + i + "' is valid"
        else:
          self.group[number] = -1
      else:
        self.group[number] = -1
      
      self.chmodf.append('')
      if parser.has_option(i, chmodf):
        self.chmodf[number] = parser.get(i, chmodf)
        if self.chmodf[number] != '':
          if checkoctalperms(self.chmodf[number], 'chmodf', i, debug):
            if len(self.chmodf[number]) == 3:
              self.chmodf[number] = '0' + self.chmodf[number]
              self.chmodf[number] = int(self.chmodf[number], 8)
            elif len(self.chmodf[number]) == 4:
              self.chmodf[number] = int(self.chmodf[number], 8)
            usowchmoderr = False
            self.doit[number] = self.doit[number] + 2
          else:
            errorsoccured = True
      
      self.chmodd.append('')  
      if parser.has_option(i, chmodd):
        self.chmodd[number] = parser.get(i, chmodd)
        if self.chmodd[number] != '':
          if checkoctalperms(self.chmodd[number], 'chmodd', i, debug):
            if len(self.chmodd[number]) == 3:
              self.chmodd[number] = '0' + self.chmodd[number]
              self.chmodd[number] = int(self.chmodd[number], 8)
            elif len(self.chmodd[number]) == 4:
              self.chmodd[number] = int(self.chmodd[number], 8)
            usowchmoderr = False 
            self.doit[number] = self.doit[number] + 4 
          else:
            errorsoccured = True
      
      self.excludedir.append([])
      if parser.has_option(i, excludedir):
        exvalid = True
        self.excludedir[number] = parser.get(i, excludedir).split(',')
        for nr, item in enumerate(self.excludedir[number]):
          item = item.strip().rstrip('/')
          self.excludedir[number][nr] = item
          if item == '':
            self.excludedir[number].remove(item)
          else:
            if not os_path.isdir(item) and not os_path.isfile(item):
              print >> sys.stderr, "\033[31;1mError in section", i + ": 'excludedir'", item, "doesn't exist.\033[0m"
              errorsoccured = True
              exvalid = False
        if exvalid == True:
          if self.dirname[number] in self.excludedir[number]:
            print >> sys.stderr, "\033[31;1mError in section", i + ": 'excludedir'", item, "is the same like 'dirname'.\033[0m"
            errorsoccured = True
          if debug == True:
            print "'excludedir' in section '" + i + "' is valid"
        if self.excludedir[number] == [] or self.excludedir[number] == ['']:
          self.excludedir[number] = None
      else:
        self.excludedir[number] = None
      
      self.excludepattern.append('')
      if parser.has_option(i, excludepattern):
        exvalid = True
        self.excludepattern[number] = parser.get(i, excludepattern)
        try:
          re_compile(self.excludepattern[number])
        except:
          print >> sys.stderr, "\033[31;1mError in section", i + ": 'excludepattern' must be a regular expression.\033[0m"
          errorsoccured = True
        else:
          if debug == True:
            print "'excludepattern' in section '" + i + "' is valid"
        if self.excludepattern[number] == '':
          self.excludepattern[number] = None
      else:
        self.excludepattern[number] = None
      
      if usowchmoderr == True:
        print >> sys.stderr, "\033[31;1mError in section", i + ": With your actual configuration, experms will do exactly nothing.\033[0m"
        errorsoccured = True
    
    if errorsoccured == True:
      print >> sys.stderr, "\033[31;1mAborting!\033[0m"
      sys.exit(1)