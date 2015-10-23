# -*- coding: utf-8 -*-

import pyinotify
import os
from action.prepare_files import prepare

class EventHandler(pyinotify.ProcessEvent):
    """
    Taken from
    www.saltycrane.com/blog/2010/04/monitoring-filesystem-python-and-pyinotify/
    """

    def __init__(self, debug):
        self.debug = debug

    def process_IN_ACCESS(self, event):
        # not watched
        pass

    def process_IN_ATTRIB(self, event):
        print event.pathname, "IN_ATTRIB", event.dir
        prepare(event.pathname, "IN_ATTRIB", event.dir, self.debug)

    def process_IN_CLOSE_NOWRITE(self, event):
        # not watched
        pass

    def process_IN_CLOSE_WRITE(self, event):
        # not watched
        pass

    def process_IN_CREATE(self, event):
        print event.pathname, "IN_CREATE", event.dir
        pass
        prepare(event.pathname, "IN_CREATE", event.dir, self.debug)

    def process_IN_DELETE(self, event):
        # not watched
        pass

    def process_IN_MODIFY(self, event):
        print event.pathname, "IN_MODIFY", event.dir
        prepare(event.pathname, "IN_MODIFY", event.dir, self.debug)

    def process_IN_OPEN(self, event):
        # not watched
        pass

    def process_IN_MOVE_SELF(self, event):
        # not watched
        pass

    def process_IN_MOVED_TO(self, event):
        prepare(event.pathname, "IN_MOVED_TO", event.dir, self.debug)
        if event.dir:
            # handle all nested files in event.filename
            for root, dirnames, filenames in os.walk(event.pathname):
                for filename in filenames:
                    filenamewrite = os.path.join(root, filename)
                    print filenamewrite, "IN_MOVED_TO", False
                    prepare(filenamewrite, "IN_MOVED_TO", False, self.debug)
                for dirname in dirnames:
                    dirnamewrite = os.path.join(root, dirname)
                    print dirnamewrite, "IN_MOVED_TO", True
                    prepare(dirnamewrite, "IN_MOVED_TO", True, self.debug)
        print event.pathname, "IN_MOVED_TO", event.dir

