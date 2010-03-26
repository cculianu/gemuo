#
#  GemUO
#
#  (c) 2005-2010 Max Kellermann <max@duempel.org>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 2 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#

import os

class TimerEvent:
    """Base class for a timer event: the tick() method is called after
    enough time has elapsed."""

    def __init__(self, manager):
        self.__manager = manager

    def _schedule(self, delay):
        self.due = os.times()[4] + delay
        self.__manager.schedule(self)

    def _unschedule(self):
        self.__manager.unschedule(self)
        self.due = None

    def tick(self):
        """Implement this."""
        assert False
