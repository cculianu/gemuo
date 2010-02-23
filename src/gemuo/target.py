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

from gemuo.engine import Engine
from gemuo.timer import TimerEvent

class TargetMutex(Engine, TimerEvent):
    TIMEOUT = 5

    def __init__(self, client):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self._locked = False
        self._abort_func = None
        self._queue = []

    def _next(self):
        assert self._locked

        if len(self._queue) == 0:
            self._locked = False
            self._abort_func = None
        else:
            self._schedule(self.TIMEOUT)
            x, self._queue = self._queue[0], self._queue[1:]
            func, self._abort_func = x
            func()

    def get_target(self, func, abort_func):
        if self._locked:
            # someone else has got the target: append to queue
            self._queue.append((func, abort_func))
        else:
            # call immediately
            self._schedule(self.TIMEOUT)
            self._locked = True
            self._abort_func = abort_func
            func()

    def put_target(self):
        assert self._locked

        self._unschedule()
        self._next()

    def tick(self):
        assert self._locked

        print "Target timeout"

        self._abort_func()
        self._next()
