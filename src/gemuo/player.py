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

from uo.skills import SKILL_NAMES
from uo.entity import *
import uo.packets as p
from gemuo.entity import Position

class SkillValue:
    def __init__(self, id, value, base, lock, cap):
        self.id = id
        self.value = value
        self.base = base
        self.lock = lock
        self.cap = cap

    def name():
        if self.id in SKILL_NAMES:
            return SKILL_NAMES[self.id]
        else:
            return str(self.id)

class WalkQueue:
    def __init__(self):
        self.clear()

    def length(self):
        return len(self._queue)

    def _next_seq(self):
        seq = self._seq
        self._seq += 1
        if self._seq >= 0x100:
            self._seq = 1
        return seq

    def request(self):
        if len(self._queue) >= 3:
            return None

        seq = self._next_seq()
        self._queue.append(seq)
        return seq

    def ack(self, seq):
        while len(self._queue) > 0:
            i, self._queue = self._queue[0], self._queue[1:]
            if i == seq:
                return True
        return False

    def clear(self):
        self._queue = []
        self._seq = 0

    def reject(self, seq):
        self.clear()

class Walk:
    def __init__(self, mobile):
        self._mobile = mobile
        self._queue = WalkQueue()

    def finished(self):
        return self._queue.length() == 0

    def walk(self, direction):
        assert isinstance(direction, int)

        seq = self._queue.request()
        if seq is None: return None

        self._move_player(direction & 0x7)
        return p.WalkRequest(direction, seq)

    def walk_reject(self, seq, x, y, z, direction):
        self._queue.reject(seq)
        self._mobile.position = Position(x, y, z, direction)

    def walk_ack(self, seq, notoriety):
        if not self._queue.ack(seq):
            # XXX resync when seq mismatch?
            print "WalkAck out of sync"

    def _move_player(self, direction):
        oldpos = self._mobile.position
        if oldpos.direction == direction:
            x, y = oldpos.x, oldpos.y
            if direction == NORTH:
                y -= 1
            elif direction == NORTH_EAST:
                x += 1
                y -= 1
            elif direction == EAST:
                x += 1
            elif direction == SOUTH_EAST:
                x += 1
                y += 1
            elif direction == SOUTH:
                y += 1
            elif direction == SOUTH_WEST:
                x -= 1
                y += 1
            elif direction == WEST:
                x -= 1
            elif direction == NORTH_WEST:
                x -= 1
                y -= 1

            self._mobile.position = Position(x, y, oldpos.z, direction)
        else:
            self._mobile.position = Position(oldpos.x, oldpos.y, oldpos.z,
                                             direction)

    def move_player(self, direction):
        self._queue.clear()
        self._move_player(direction)
