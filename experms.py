#!/usr/bin/env python2
# -*- coding: utf-8 -*-

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

"""
         FILE: experms.py

        USAGE: experms.py [start|stop|restart|restore|status|log|err|
               dircount|(help|-h|--help)|version|foreground|debug [file]]

  DESCRIPTION: Runs as daemon and monitors file-changes happened in the
               directory set in experms.conf.
               If changes happened, it adjusts the file-permissions and
               ownership/group.
               You can either define one directory, or several directories
               with different ownerships and permissions.
               It also allows exclusions based on directories or patterns
               (regex).
               Further it is able to restore all the ownerships and
               permissions of all files based on the config-file.
               experms supports multiple instances, but only one per user.

       CONFIG: experms.conf

 REQUIREMENTS: python2, python2-pyinotify, python2-psutil

        NOTES: Experms uses inotify to monitor the directories.
               Inotify allows only a limited number of directories to watch
               per user. Per default this is set to 8192.
               You can increase this number by writing to
               /proc/sys/fs/inotify/max_user_watches
               To make this change permanent, the following line should be
               added to (depending on your setup) /etc/sysctl.conf or
               /etc/sysctl.d/99-sysctl.conf
               You can check the number of directories recursively with:
               'experms.py dircount'

       AUTHOR: Fabio Rämi - fabio(at)dynamix-tontechnik(dot)ch

      VERSION: 0.8

      LICENCE: GNU GPL v3.0 or later.
               http://www.gnu.org/licenses/gpl-3.0.txt
               Experms comes with absolutely no warranty!

      COPYING: Experms is free software: you can redistribute it and/or
               modify it under the terms of the GNU General Public License as
               published by the Free Software Foundation, either version 3 of
               the License, or (at your option) any later version.

               Experms is distributed in the hope that it will be useful,
               but WITHOUT ANY WARRANTY; without even the implied warranty of
               MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
               GNU General Public License for more details.

               You should have received a copy of the GNU General Public
               License along with Experms.  If not, see
               <http://www.gnu.org/licenses/>.

      CREATED: 2013
               2014
"""

# bold: "\033[1m"
# green: "\033[32;1m"
# red: "\033[31;1m"
# normal: "\033[0m"

import sys
import os
from re import compile as re_compile
from time import localtime, strftime, sleep, time
from daemon import Daemon
import check_config
try:
    import pyinotify
except ImportError:
    print >> sys.stderr, ("\033[31;1mError: Module pyinotify not found. Please"
                          "install the package 'python2-pyinotify'.\nMaybe "
                          "this package is called differently in your "
                          "distribution (e.g. python2.7-pyinotify).\033[0m")
    sys.exit(1)
try:
    import psutil
except ImportError:
    print >> sys.stderr, ("\033[31;1mError: Module psutil not found. Please "
                          "install the package 'python2-psutil'.\nMaybe this "
                          "package is called differently in your distribution "
                          "(e.g. python2.7-psutil).\033[0m")
    sys.exit(1)

# set default and global variables
exversion = '0.8'
debug = False
daemon = None
config = None
restoreerror = 0
allcounts = None
uid = os.geteuid()
pidfile = '/tmp/experms_' + str(uid) + '.pid'
if uid == 0:
    stdoutfile = '/var/log/experms.log'
    stderrfile = '/var/log/experms.err'
else:
    home = os.path.expanduser("~")
    stdoutfile = home + '/.experms.log'
    stderrfile = home + '/.experms.err'

class MyDaemon(Daemon):
    """
    Taken from Sander Marechal
    (www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/)
    """
    def start(self):
        """
        Start the daemon
        """

        # check if experms is already running
        isrunning = checkpid()
        if not isrunning == False:
            sys.stderr.write("Experms is already running with PID %s\n"
                             % isrunning)
            sys.exit(1)
        # load the configuration
        config = self.loadconfig()
        if config.restore == 'yes':
            restore()
        dircount()
        print "\033[32;1mExperms daemon started.\033[0m"
        # Start the daemon
        self.daemonize()
        self.run()

    def loadconfig(self):
        """
        Load the configuration file.
        """
        global config
        config = check_config.Check(uid, debug)
        return config

    def run(self):
        """
        Start pyinotify
        """
        # do not use IN_MOVED_SELF! It will burn down your house!
        mask = (pyinotify.IN_CREATE | pyinotify.IN_MODIFY |
                pyinotify.IN_ATTRIB | pyinotify.IN_MOVED_TO) # watched events

        # watch manager
        wm = pyinotify.WatchManager()
        notifier = pyinotify.ThreadedNotifier(wm, MyEventHandler())

        # Start the notifier from a new thread, without doing anything as no
        # directory or file is currently monitored yet.
        notifier.start()
        # Start watching the paths
        wdd = wm.add_watch(config.dirname, mask, rec=True, auto_add=True)

        # handle quit when running in foreground
        try:
            while True:
                sleep(0.05)
        except KeyboardInterrupt:
            # happens when the user presses ctrl-c
            wm.rm_watch(wdd.values())
            notifier.stop()
            print "\nBye-bye!"
            sys.exit(0)
        except EOFError:
            # happens when the user presses ctrl-d
            wm.rm_watch(wdd.values())
            notifier.stop()
            print "\nBye-bye!"
            sys.exit(0)

class MyEventHandler(pyinotify.ProcessEvent):
    """
    Taken from
    www.saltycrane.com/blog/2010/04/monitoring-filesystem-python-and-pyinotify/
    """
    def process_IN_ACCESS(self, event):
        # not watched
        pass

    def process_IN_ATTRIB(self, event):
        prepare(event.pathname, "ATTRIB")

    def process_IN_CLOSE_NOWRITE(self, event):
        # not watched
        pass

    def process_IN_CLOSE_WRITE(self, event):
        # not watched
        pass

    def process_IN_CREATE(self, event):
        prepare(event.pathname, "CREATE")

    def process_IN_DELETE(self, event):
        # not watched
        pass

    def process_IN_MODIFY(self, event):
        prepare(event.pathname, "MODIFY")

    def process_IN_OPEN(self, event):
        # not watched
        pass

    def process_IN_MOVE_SELF(self, event):
        # not watched
        pass

    def process_IN_MOVED_TO(self, event):
        prepare(event.pathname, "IN_MOVED_TO")
        # handle all nested files in event.filename
        for root, dirnames, filenames in os.walk(event.pathname):
            for filename in filenames:
                filenamewrite = os.path.join(root, filename)
                prepare(filenamewrite, "IN_MOVED_TO")
            for dirname in dirnames:
                dirnamewrite = os.path.join(root, dirname)
                prepare(dirnamewrite, "IN_MOVED_TO")

def prepare(directory, event=None, restore=False):
    """
    Prepare everything:
     - Check what rule has to be applied
     - Check if the file is excluded
    """
    if debug == True:
        print ('[DEBUG] ' + strftime("%Y-%m-%d_%H:%M:%S", localtime()) +
               "%.20f" % time() + ' event to process:', event, directory)

    dirhighest = 0
    for nr, item in enumerate(config.dirname):
        tempdirhighest = 0
        if not item in directory:
            continue
        for count, thing in enumerate(directory.split('/')):
            try:
                item.split('/')[count]
            except IndexError:
                break
            if thing == item.split('/')[count]:
                tempdirhighest = tempdirhighest + 1
        if tempdirhighest > dirhighest:
            dirhighest = tempdirhighest
            ruledir = nr

    # check if the file is excluded or what rules have to take effect
    if not config.excludepattern[nr] == None:
        if os.path.isfile(directory):
            p = re_compile(config.excludepattern[nr])
            if p.search(os.path.basename(directory)):
                return
    if config.excludedir[nr] == None:
        highest = 0
    else:
        highest = 0
        for item in config.excludedir[nr]:
            if not item in directory:
                continue
            temphighest = 0
            for nr, thing in enumerate(directory.split('/')):
                try:
                    item.split('/')[nr]
                except IndexError:
                    break
                if thing == item.split('/')[nr]:
                    temphighest = temphighest + 1
            if temphighest > highest:
                highest = temphighest

    if highest > dirhighest:
        return

    action(directory, event, ruledir, restore)

def collect_filenames():
    """
    collects all the filenames in the monitored directories
    returns an array: [[filenames],[dirnames],[allnames],count]
    """
    sys.stdout.write("Counting directories...")

    realdirs = []
    for item in config.dirname:
        doappend = True
        for thing in config.dirname:
            if not item == thing:
                p = re_compile('^' + thing + '/')
                if p.search(item):
                    doappend = False
                    break
        if doappend == True:
            realdirs.append(item)

    matchesfile = []
    matchesdir = []
    matchesall = []
    for item in realdirs:
        for root, dirnames, filenames in os.walk(item):
            for filename in filenames:
                filenamewrite = os.path.join(root, filename)
                matchesfile.append(filenamewrite)
                matchesall.append(filenamewrite)
            for dirname in dirnames:
                dirnamewrite = os.path.join(root, dirname)
                matchesdir.append(dirnamewrite)
                matchesall.append(dirnamewrite)
    # Add the watched dirs to the lists
    for thing in realdirs:
        matchesdir.append(thing)
        matchesall.append(thing)
    sys.stdout.write(" Done.\n")
    sys.stdout.flush()
    return [matchesfile, matchesdir, matchesall, len(matchesdir)]

def dircount():
    """
    outputs the file count alongside the inotify limit.
    """
    global allcounts

    if allcounts == None:
        allcounts = collect_filenames()

    inotifynumber = check_inotify_config()
    print ("Total count of directories (including subdirectories) you have "
           "configured to monitor:")
    print "\033[32;1m" + str(allcounts[3]) + "\033[0m"
    print "Amount of allowed directories to watch per user (inotify):"
    print "\033[32;1m" + str(inotifynumber) + "\033[0m"
    if allcounts[3] >= int(inotifynumber):
        if uid == 0:
            print >> sys.stderr, ("\033[31;1mYou need to edit "
                                  "'/proc/sys/fs/inotify/max_user_watches', in"
                                  " order to allow more directories to watch."
                                  "\nTo make this change permanent, the "
                                  "following line should be added to "
                                  "/etc/sysctl.conf\nor /etc/sysctl.d/99-"
                                  "sysctl.conf:\nfs.inotify.max_user_watches="
                                  "8192 (your amount of directories)\033[0m")
            sys.exit(1)
        else:
            print >> sys.stderr, ("\033[31;1mAsk the system-administrator to "
                                  "edit '/proc/sys/fs/inotify/max_user_watches"
                                  "', in order to allow more directories to "
                                  "watch.\nTo make this change permanent, the "
                                  "following line should be added to "
                                  "/etc/sysctl.conf\nor /etc/sysctl.d/99-"
                                  "sysctl.conf:\nfs.inotify.max_user_watches="
                                  "8192 (your amount of directories)\033[0m")
            sys.exit(1)
    elif allcounts[3] > int(inotifynumber) - 2000:
        if uid == 0:
            print ("\033[31;1mYou have possibly hit your limit of watched "
                   "directories or will very soon.\nEdit '/proc/sys/fs/inotify"
                   "/max_user_watches',\nin order to allow more directories to"
                   " watch.\nTo make this change permanent, the following line"
                   " should be added to /etc/sysctl.conf\nor /etc/sysctl.d/99-"
                   "sysctl.conf:\nfs.inotify.max_user_watches=8192 (your "
                   "amount of directories)\nIf you encounter any problems, "
                   "check '" + sys.argv[0] + " err' for errors.\033[0m")
        else:
            print ("\033[31;1mYou have possibly hit your limit of watched "
                   "directories or will very soon.\nAsk the system-"
                   "administrator to edit '/proc/sys/fs/inotify/max_user_"
                   "watches',\nin order to allow more directories to watch.\n"
                   "To make this change permanent, the following line should "
                   "be added to /etc/sysctl.conf\nor /etc/sysctl.d/99-sysctl."
                   "conf:\nfs.inotify.max_user_watches=8192 (your amount of "
                   "directories)\nIf you encounter any problems, check '" +
                   sys.argv[0] + " err' for errors.\033[0m")

def check_inotify_config():
    """
    Check the amount of watchable files in the inotify config
    """
    with open('/proc/sys/fs/inotify/max_user_watches', 'r') as inotifyconf:
        return inotifyconf.read().strip()

def restore():
    """
    Restores all the ownerships and permissions on all files
    """
    global allcounts
    allcounts = collect_filenames()
    # handle ugly output with debug
    if debug == True:
        print "Restore is in progress..."
    else:
        sys.stdout.write("Restore is in progress...")
    for item in allcounts[2]:
        prepare(item, 'restore', True)
    if debug == True:
        print "Done."
    else:
        sys.stdout.write(" Done.\n")
        sys.stdout.flush()
    try:
        restorelogcount = saferestorelog()
    except NameError:
        restorelogcount = 0
    print ("\033[32;1m" + str(restorelogcount) + " files have been changed."
           "\033[0m")
    if restoreerror > 0:
        print ("\033[31;1m" + str(restoreerror) + " errors occured.\nCheck '" +
               sys.argv[0] + " err' for details.\nAborting!\033[0m")
        sys.exit(1)

def action(directory, event, ruledir, restore):
    """
    Finally do what we're here for.
    """
    global restoreerror
    try:
        # use os.lstat instead of os.stat in order to not following symlinks
        actpermsraw = os.lstat(directory)
    except OSError, e:
        if e.errno == 13:
            errmessage = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) +
                          " Permission denied for '" + directory + "'")
            if not restore == True or debug == True:
                print >> sys.stderr, errmessage
            else:
                with open(stderrfile, "a") as errfile:
                    errfile.write(errmessage + '\n')
            restoreerror = restoreerror + 1
            return
        elif e.errno == 2:
            # this means the file/directory doesn't exist anymore
            return

    actperms = ([actpermsraw.st_uid, actpermsraw.st_gid,
                 oct(actpermsraw.st_mode & 0777)])
    # change owner and group
    changedchown = False
    changedchmod = False

    # do the chowning
    if config.doit[ruledir] in (1, 3, 5, 7):
        if config.owner[ruledir] == -1:
            realowner = actperms[0]
        else:
            realowner = config.owner[ruledir]
        if config.group[ruledir] == -1:
            realgroup = actperms[1]
        else:
            realgroup = config.group[ruledir]
        if not actperms[0] == realowner or not actperms[1] == realgroup:
            try:
                os.lchown(directory, realowner, realgroup)
                changedchown = True
            except OSError, e:
                if e.errno == 13:
                    changedchown = False
                    errmessage = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) +
                                  " Permission denied for '" + directory + "'")
                    if not restore == True or debug == True:
                        print >> sys.stderr, errmessage
                    else:
                        with open(stderrfile, "a") as errfile:
                            errfile.write(errmessage + '\n')
                    restoreerror = restoreerror + 1
                    return
                elif e.errno == 2:
                    # this means the file/directory doesn't exist anymore
                    return
                elif e.errno == 1:
                    changedchown = False
                    errmessage = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) +
                                  " Operation not permitted for '" + directory
                                  + "'")
                    if not restore == True or debug == True:
                        print >> sys.stderr, errmessage
                    else:
                        with open(stderrfile, "a") as errfile:
                            errfile.write(errmessage + '\n')
                    restoreerror = restoreerror + 1
                    return
                else:
                    changedchown = False
                    errmessage = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) +
                                  " An unexpected Error occured for '" +
                                  directory + "'")
                    if not restore == True or debug == True:
                        print >> sys.stderr, errmessage
                    else:
                        with open(stderrfile, "a") as errfile:
                            errfile.write(errmessage + '\n')
                    restoreerror = restoreerror + 1
                    return
            except:
                changedchown = False
                errmessage = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) +
                              " An unexpected Error occured for '" +
                              directory + "'")
                if not restore == True or debug == True:
                    print >> sys.stderr, errmessage
                else:
                    with open(stderrfile, "a") as errfile:
                        errfile.write(errmessage + '\n')
                restoreerror = restoreerror + 1
                return

    # do the chmodding
    try:
        if (os.path.isfile(directory) and config.doit[ruledir] in (2, 3, 6, 7)
                and not os.path.islink(directory) and not int(actperms[2], 8)
                == config.chmodf[ruledir]):
            os.chmod(directory, config.chmodf[ruledir])
            changedchmod = True
        elif (os.path.isdir(directory) and config.doit[ruledir] in (4, 5, 6, 7)
              and not os.path.islink(directory) and not int(actperms[2], 8)
              == config.chmodd[ruledir]):
            os.chmod(directory, config.chmodd[ruledir])
            changedchmod = True
    except OSError, e:
        if e.errno == 13:
            changedchmod = False
            errmessage = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) +
                          " Permission denied for '" + directory + "'")
            if not restore == True or debug == True:
                print >> sys.stderr, errmessage
            else:
                with open(stderrfile, "a") as errfile:
                    errfile.write(errmessage + '\n')
            restoreerror = restoreerror + 1
            return
        elif e.errno == 2:
            # this means the file/directory doesn't exist anymore
            return
        else:
            changedchmod = False
            errmessage = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) +
                          " An unexpected Error occured for '" + directory +
                          "'")
            if not restore == True or debug == True:
                print >> sys.stderr, errmessage
            else:
                with open(stderrfile, "a") as errfile:
                    errfile.write(errmessage + '\n')
            restoreerror = restoreerror + 1
            return
    except:
        changedchmod = False
        errmessage = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) +
                      " An unexpected Error occured for '" + directory + "'")
        if not restore == True or debug == True:
            print >> sys.stderr, errmessage
        else:
            with open(stderrfile, "a") as errfile:
                errfile.write(errmessage + '\n')
        restoreerror = restoreerror + 1
        return

    # do the logging
    if True in [changedchown, changedchmod]:
        if config.logit == 'yes':
            logging(directory, restore, ruledir, event)
        else:
            if 'foreground' == sys.argv[1]:
                logging(directory, restore, ruledir, event)

    sys.stdout.flush()

def logging(directory, restore, ruledir, event):
    """
    writes the logfile
    """
    if not debug:
        logtext = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ' Section: ' +
                   config.sectionname[ruledir] + ' Event: ' + event + ' ' +
                   directory)
    else:
        logtext = (strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ' ' + "%.20f" %
                   time() + ' Section: ' + config.sectionname[ruledir] +
                   ' Event: ' + event + ' ' + directory)
    if restore == False:
        if not 'foreground' == sys.argv[1] and not 'debug' == sys.argv[1]:
            if not os.path.isfile(stdoutfile):
                daemon.mknewlog()
            if not os.path.isfile(stderrfile):
                daemon.mknewerr()
        print logtext
    else:
        if debug == True:
            print logtext
        else:
            with open(stdoutfile, "a") as logfile:
                logfile.write(logtext + '\n')
            global restorelogcount
            try:
                restorelogcount
            except NameError:
                restorelogcount = 1
            else:
                restorelogcount = restorelogcount + 1
            saferestorelog(restorelogcount)

def saferestorelog(count=None):
    """
    safe the count of processed files by the restore function
    to output it in the end
    """
    if not count == None:
        global givecountback
        givecountback = count
    else:
        try:
            givecountback
        except NameError:
            givecountback = 0
        return givecountback

def checkpid():
    """
    Check for a pidfile to see if the daemon already runs
    If PID-file exists, check with psutil if experms is really running
    """
    try:
        pf = file(pidfile, 'r')
        pid = int(pf.read().strip())
        pf.close()
    except IOError:
        pid = None
    if not pid:
        return False
    try:
        psutil.Process(pid)
    except psutil._error.NoSuchProcess:
        os.remove(pidfile)
        return False
    else:
        if (psutil.Process(pid).uids().effective == uid and
                psutil.Process(pid).name() == 'experms'):
            return pid
        else:
            os.remove(pidfile)
            return False


def usage(command):
    print ("usage: %s [start|stop|restart|restore|status|log|err|dircount|"
           "(help|-h|--help)|version|foreground|debug [file]]" % command)
    print "See 'man experms' or the README file for more information."

def set_procname(newname):
    """
    Change the name of the process to 'experms'.
    From blog.abhijeetr.com/2010/10/changing-process-name-of-python-script.html
    """
    from ctypes import cdll, byref, create_string_buffer
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

def print_version():
    print "\033[32;1mExperms v" + exversion + "\033[0m"

def norootwarn():
    if not uid == 0:
        print ("\033[31;1mYou are about to start experms without "
               "root-permissions.\nPlease keep in mind, that this is subject "
               "to restrictions. See 'man experms' for more information."
               "\033[0m")

def main():
    global config
    global daemon
    global debug

    set_procname('experms')
    daemon = MyDaemon(pidfile, '/dev/null', stdoutfile, stderrfile)
    if len(sys.argv) == 2 or len(sys.argv) == 3:
        if len(sys.argv) == 3:
            if not sys.argv[1] == 'debug':
                print_version()
                usage(sys.argv[0])
                sys.exit(1)
        if 'start' == sys.argv[1]:
            print_version()
            norootwarn()
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print_version()
            stoped = daemon.stop()
            if not stoped == False:
                print "\033[32;1mExperms stopped.\033[0m"
        elif 'restart' == sys.argv[1]:
            print_version()
            print "Experms is restarting."
            norootwarn()
            daemon.restart()
        elif 'restore' == sys.argv[1]:
            print_version()
            norootwarn()
            config = daemon.loadconfig()
            restore()
            try:
                restorelogcount
            except NameError:
                restorelogcount = 0
            print restorelogcount, 'files have been changed.'
        elif 'status' == sys.argv[1]:
            # Check for a pidfile to see if the daemon is running
            isrunning = checkpid()
            if not isrunning == False:
                print ("\033[32;1mExperms v" + exversion + " is running with "
                       "the PID " + str(isrunning) + ".\033[0m")
                config = daemon.loadconfig()
                dircount()
                sys.exit(0)
            else:
                print ("\033[32;1mExperms v" + exversion +
                       " is not running.\033[0m")
                sys.exit(1)
        elif 'log' == sys.argv[1]:
            print_version()
            if not os.path.isfile(stdoutfile):
                print "There is no logfile to show yet."
            elif os.stat(stdoutfile)[6] == 0:
                print "There is no logfile to show yet."
            from subprocess import call
            print "\033[32;1mCalling 'tail -F", stdoutfile + "':\033[0m"
            try:
                call(["tail", "-F", stdoutfile])
            except KeyboardInterrupt:
                sys.exit(0)
        elif 'err' == sys.argv[1]:
            print_version()
            if not os.path.isfile(stderrfile):
                print "There is no logfile to show yet."
            elif os.stat(stderrfile)[6] == 0:
                print "There is no logfile to show yet."
            from subprocess import call
            print "\033[32;1mCalling 'tail -F", stderrfile + "':\033[0m\n"
            try:
                call(["tail", "-F", stderrfile])
            except KeyboardInterrupt:
                sys.exit(0)
        elif 'dircount' == sys.argv[1]:
            print_version()
            config = daemon.loadconfig()
            dircount()
        elif ('-h' == sys.argv[1] or '--help' == sys.argv[1] or
              'help' == sys.argv[1]):
            print_version()
            usage(sys.argv[0])
            sys.exit(0)
        elif 'version' == sys.argv[1]:
            print_version()
        elif 'foreground' == sys.argv[1] or 'debug' == sys.argv[1]:
            if 'debug' == sys.argv[1]:
                debug = True
                if len(sys.argv) == 3:
                    print_version()
                    print 'Starting experms in debug mode.'
                    print 'All output will be written to ' + sys.argv[2]
                    print 'Press Ctrl+c to exit.'
                    try:
                        dfile = open(sys.argv[2], 'a+', 0)
                        os.dup2(dfile.fileno(), sys.stdout.fileno())
                        os.dup2(dfile.fileno(), sys.stderr.fileno())
                    except IOError:
                        print ("\033[31;1mError opening " + sys.argv[2] +
                               "!\033[0m")
                        sys.exit(1)
            print_version()
            norootwarn()

            # Check for a pidfile to see if the daemon is running
            isrunning = checkpid()
            if not isrunning == False:
                sys.stderr.write("Experms is already running with PID %s\n"
                                 % isrunning)
                sys.exit(1)

            config = daemon.loadconfig()

            if config.restore == 'yes':
                restore()

            dircount()
            print "Experms started in foreground.\nPress ctrl+c to exit."
            daemon.run()
        else:
            print_version()
            print >> sys.stderr, "Unknown command"
            usage(sys.argv[0])
            sys.exit(1)
        sys.exit(0)
    else:
        print_version()
        usage(sys.argv[0])
        sys.exit(1)


if __name__ == "__main__":
    main()
