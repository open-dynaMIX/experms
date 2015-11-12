#experms
Distributed under the GNU GPL  
http://www.gnu.org/licenses/gpl-3.0.txt  
Or see the file ./COPYING

##Introduction
Monitors file-changes happened in the directory set in experms.conf. If changes  
happened, it adjusts the file-permissions and ownership/group.

You can either define directories (and also sub-directories) with different  
ownerships and permissions.

It also allows exclusions based on directories or patterns (regex).  
Further it is able to restore all the ownerships and permissions of all files  
based on the config-file.

experms needs to be run with root-permissions.


##Dependencies
experms depends on:
 - python2
 - python2-pyinotify (name can vary on different Linux distributions)
 - systemd (optional)


##Usage
You can start and/or enable experms with systemd:  
```
# systemctl start experms
# systemctl enable experms
```

Following arguments are available:

```
usage: experms [-h] [-c CONFIG] [-r] [-t] [-v] [-d]

experms

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration file to use
  -r, --restore         Just restore all the permissions and exit
  -t, --total           Count the directories to watch and exit
  -v, --version         Print the version and exit
  -d, --debug           Print debug-messages

```


Note: You need to edit the configuration file before running experms for the  
      first time!


##The Configuration File
experms.conf is located under /etc/experms.conf  
You can use another file with the argument '--config'.

If changes happened to experms.conf, it is necessary to restart  
experms.

###Example
```
#
# /etc/experms.conf
#

[general]
log_activities = no
restore = no

[DEFAULT]
chmodd = 755

[directory_1]
path = /first/directory
user = first-user
group = first-group
chmodf = 640
chmodd = g+w
excludepath = /first/directory/exclude1,/first/directory/subdir/exclude2

[directory_2]
path = /second/directory
group = second-group
chmodf = 0644
excludepattern = .txt$|.TXT$|.sh$|.SH$

[directory_3]
path = /second/directory/subdirectory
group = third-group
chmodf = g+w,o-r
chmodd = g+w,o-rx
```

###General Section
log_activities = yes | no  
Decide, if experms should print a log.

restore = yes | no  
Decide, if experms should restore all the ownerships and permissions  
of all files based on the config-file. In case there were changes  
while experms was not running.

###Default Section
Rules that should apply to all directory sections. They can be over‐  
written inside a directory section.

###Directory Section
**path = /path/to/watch/dir**  
Set the directory where your rules should apply.

**owner = username|UID**  
Set the owner of all the files and directories.

**group = groupname|GID**  
Set the group of all the files and directories.

**chmodf = permissions**  
Set the permission for all the files.  
Accepted is octal (0777) or symbolic mode (comma separated list).  
Symbolic mode has limited functionality and only supports  
[ugoa][+-=][rwxugo]  
You can use set-UID, set-GID and sticky-bit if you wish to. E.g. 4660.

**chmodd = permissions**  
Set the permission of all the directories.  
See chmodf above.

**excludepath = /path/to/exclude/dir,/path/to/exclude/file...**  
Exclude some directories and files from the rules (comma  seperated).

**excludepattern = regular expression**  
Exclude files (and only files) based on a pattern.


##Inotify Configuration
experms uses inotify to monitor the directories.  
Inotify allows only a limited number of directories to watch per user.  
Per default this is set to 8192.  
You can increase this number by writing to `/proc/sys/fs/inotify/max_user_watches`  
To make this change permanent, the following line should be added to  
/etc/sysctl.conf or /etc/sysctl.d/99-sysctl.conf  
`fs.inotify.max_user_watches=8192` (your amount of directories)

You can check the amount of directories recursively with:

`# experms --total`
