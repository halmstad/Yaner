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
This module contains the L{Presentable} class of L{yaner}.
"""

import os
import gobject

from yaner.Task import Task
from yaner.Constants import U_CONFIG_DIR
from yaner.utils.Logging import LoggingMixin
from yaner.utils.Configuration import ConfigParser

class Presentable(LoggingMixin, gobject.GObject):
    """
    The Presentable class of L{yaner}, which provides data for L{PoolModel}.
    """

    __gsignals__ = {
            'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            'removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
            'task-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (Task,)),
            'task-removed': (gobject.SIGNAL_RUN_LAST,
                gobject.TYPE_NONE, (Task,)),
            'task-changed': (gobject.SIGNAL_RUN_LAST,
                gobject.TYPE_NONE, (Task,)),
            }
    """
    GObject signals of this class.
    """

    _CONFIG_DIR = os.path.join(U_CONFIG_DIR, 'presentables')
    """
    User config directory containing presentable configuration files.
    """

    def __init__(self, uuid_, default_config):
        LoggingMixin.__init__(self)
        gobject.GObject.__init__(self)

        self._default_config = default_config
        self._uuid = uuid_
        self._config = None
        self._tasks = []

    @property
    def uuid(self):
        """Get the uuid of the presentable."""
        return self.config.file

    @property
    def config(self):
        """
        Get the configuration of the presentable.
        If the file doesn't exist, read from the default configuration.
        If the presentable configuration directory doesn't exist, create it.
        """
        if self._config is None:
            config = ConfigParser(self._CONFIG_DIR, self._uuid)
            if config.empty():
                self.logger.info(
                        _('No presentable configuration file, creating...'))
                config.update(self._default_config)
            self._config = config
        return self._config

    @property
    def tasks(self):
        """Get the tasks of the presentable."""
        return self._tasks

