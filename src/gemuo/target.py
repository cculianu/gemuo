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

from twisted.internet import reactor
import uo.packets as p
from gemuo.engine import Engine

class TargetMutex:
    TIMEOUT = 5

    def __init__(self):
        self._locked = False
        self._abort_func = None
        self._queue = []

    def _next(self):
        assert self._locked

        if len(self._queue) == 0:
            self._locked = False
            self._abort_func = None
        else:
            self.call_id = reactor.callLater(self.TIMEOUT, self._timeout)
            x, self._queue = self._queue[0], self._queue[1:]
            func, self._abort_func = x
            func()

    def get_target(self, func, abort_func):
        if self._locked:
            # someone else has got the target: append to queue
            self._queue.append((func, abort_func))
        else:
            # call immediately
            self.call_id = reactor.callLater(self.TIMEOUT, self._timeout)
            self._locked = True
            self._abort_func = abort_func
            func()

    def put_target(self):
        assert self._locked

        self.call_id.cancel()
        self._next()

    def _timeout(self):
        assert self._locked

        print "Target timeout"

        self._abort_func()
        self._next()

class Target:
    def __init__(self, serial=0, x=0xffff, y=0xffff, z=0xffff, graphic=0):
        self.serial = serial
        self.x = x
        self.y = y
        self.z = z
        self.graphic = graphic

    def __str__(self):
        l = []
        if self.serial != 0: l.append('serial=0x%x' % self.serial)
        if self.x != 0xffff: l.append('x=%d' % self.x)
        if self.y != 0xffff: l.append('y=%d' % self.y)
        if self.z != 0xffff: l.append('z=%d' % self.z)
        if self.graphic != 0: l.append('graphic=0x%x' % self.graphic)
        return '[Target %s]' % ' '.join(l)

    def response(self, target_id, flags):
        return p.TargetResponse(0, target_id, flags, self.serial,
                                self.x, self.y, self.z, self.graphic)

class SendTarget(Engine):
    def __init__(self, client, target):
        Engine.__init__(self, client)
        self.target = target

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._client.send(self.target.response(packet.target_id, packet.flags))
            self._success()
