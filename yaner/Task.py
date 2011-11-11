#!/usr/bin/env python2
# vim:fileencoding=UTF-8

# This file is part of Yaner.

# Yaner - GTK+ interface for aria2 download mananger
# Copyright (C) 2010-2011  Iven <ivenvd#gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
This module contains the L{Task} class of L{yaner}.
"""

import gobject
import sqlobject

from sqlobject.inheritance import InheritableSQLObject

from yaner.Misc import GObjectSQLObjectMeta
from yaner.utils.Logging import LoggingMixin
from yaner.utils.Enum import Enum
from yaner.utils.Notification import Notification

class Task(InheritableSQLObject, gobject.GObject, LoggingMixin):
    """
    Task class is just downloading tasks, which provides data to L{TaskListModel}.
    """

    __metaclass__ = GObjectSQLObjectMeta

    __gsignals__ = {
            'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            'removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            }
    """
    GObject signals of this class.
    """

    TYPES = Enum((
        'NORMAL',
        'BT',
        'ML',
        ))
    """
    The types of the task, which is a L{Enum<yaner.utils.Enum>}.
    C{TYPES.NAME} will return the type number of C{NAME}.
    """

    STATUSES = Enum((
        'RUNNING',
        'PAUSED',
        'COMPLETED',
        'ERROR',
        ))
    """
    The statuses of the task, which is a L{Enum<yaner.utils.Enum>}.
    C{STATUSES.NAME} will return the type number of C{NAME}.
    """

    name = sqlobject.UnicodeCol()
    status = sqlobject.IntCol(default=STATUSES.PAUSED)
    deleted = sqlobject.BoolCol(default=False)
    type = sqlobject.IntCol()
    uris = sqlobject.PickleCol(default=[])
    percent = sqlobject.FloatCol(default=0)
    size = sqlobject.IntCol(default=0)
    gid = sqlobject.StringCol(default='')
    metadata = sqlobject.PickleCol(default=None)
    options = sqlobject.PickleCol()

    pool = sqlobject.ForeignKey('Pool')
    category = sqlobject.ForeignKey('Category')

    def _init(self, *args, **kwargs):
        LoggingMixin.__init__(self)
        gobject.GObject.__init__(self)
        InheritableSQLObject._init(self, *args, **kwargs)
        self.upload_speed = '20k/s'
        self.download_speed = '10k/s'
        self.connections = 2

    @property
    def progress_text(self):
        """Get the text to show on the progress bar."""
        return '{:.2%}'.format(self.percent)

    def _on_started(self, gid):
        """Task started callback, update task information."""
        self.status = self.STATUSES.RUNNING
        self.gid = gid[-1] if isinstance(gid, list) else gid

    def _on_twisted_error(self, failure):
        """Handle errors occured when calling some function via twisted."""
        self.status = self.STATUSES.ERROR
        self.gid = ''
        Notification(_('Network Error'), failure.getErrorMessage())

class NormalTask(Task):
    """Normal Task."""

    def start(self):
        """Start the task."""
        deferred = self.pool.proxy.callRemote('aria2.addUri',
                self.uris, self.options)
        deferred.addCallbacks(self._on_started, self._on_twisted_error)

class BTTask(Task):
    """BitTorrent Task."""

    def start(self):
        """Start the task."""
        deferred = self.pool.proxy.callRemote('aria2.addTorrent',
                self.metadata, self.uris, self.options)
        deferred.addCallbacks(self._on_started, self._on_twisted_error)

class MTTask(Task):
    """Metalink Task."""

    def start(self):
        """Start the task."""
        deferred = self.pool.proxy.callRemote('aria2.addMetalink',
                self.metadata, self.options)
        deferred.addCallbacks(self._on_started, self._on_twisted_error)

