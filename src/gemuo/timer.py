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

class TimerManager:
    def __init__(self):
        self.__timers = []

    def schedule(self, timer):
        assert isinstance(timer, TimerEvent)

        if not timer in self.__timers:
            self.__timers.append(timer)
        self.__timers.sort(lambda a, b: cmp(a.due, b.due))

    def unschedule(self, timer):
        assert isinstance(timer, TimerEvent)

        self.__timers.remove(timer)

    def _tick(self):
        now = os.times()[4]
        while len(self.__timers) > 0 and self.__timers[0].due <= now:
            x, self.__timers = self.__timers[0], self.__timers[1:]
            x.tick()
