# -*- coding: utf-8 -*-

import pyinotify
import os
from action.prepare_files import prepare

class EventHandler(pyinotify.ProcessEvent):
    """
    pyinotify EventHandler
    """

    def __init__(self, config, debug):
        self.config = config
        self.debug = debug

    def process_IN_ATTRIB(self, event):
        prepare(event.pathname, "IN_ATTRIB", event.dir, self.config, self.debug)

    def process_IN_CREATE(self, event):
        prepare(event.pathname, "IN_CREATE", event.dir, self.config, self.debug)

    def process_IN_MODIFY(self, event):
        prepare(event.pathname, "IN_MODIFY", event.dir, self.config, self.debug)

    def process_IN_MOVED_TO(self, event):
        prepare(event.pathname, "IN_MOVED_TO", event.dir, self.config, self.debug)
        if event.dir:
            # handle all nested files in event.pathname
            for root, dirnames, filenames in os.walk(event.pathname):
                for filename in filenames:
                    filenamewrite = os.path.join(root, filename)
                    prepare(filenamewrite, "IN_MOVED_TO", False, self.config, self.debug)
                for dirname in dirnames:
                    dirnamewrite = os.path.join(root, dirname)
                    prepare(dirnamewrite, "IN_MOVED_TO", True, self.config, self.debug)
