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

class Walk:
    def __init__(self, mobile):
        self._mobile = mobile
        self._seq = None
        self._next_seq = 0
        self._direction = None

    def walk(self, direction):
        assert isinstance(direction, int)

        if self._mobile.position is None: return
        if self._seq is not None: return

        self._direction = direction & 0x7
        self._seq = self._next_seq
        self._next_seq += 1
        if self._next_seq >= 0x100:
            self._next_seq = 1
        return p.WalkRequest(self._direction, self._seq)

    def walk_reject(self, seq, x, y, z, direction):
        if self._mobile.position is None: return

        # XXX resync when seq mismatch?
        self._seq = None
        self._direction = None
        self._next_seq = 0
        self._mobile.position = Position(x, y, z, direction)

    def walk_ack(self, seq, notoriety):
        if self._mobile.position is None: return

        if self._seq != seq:
            # XXX resync when seq mismatch?
            pass

        oldpos = self._mobile.position
        if oldpos.direction == self._direction:
            x, y = oldpos.x, oldpos.y
            if self._direction == NORTH:
                y -= 1
            elif self._direction == NORTH_EAST:
                x += 1
                y -= 1
            elif self._direction == EAST:
                x += 1
            elif self._direction == SOUTH_EAST:
                x += 1
                y += 1
            elif self._direction == SOUTH:
                y += 1
            elif self._direction == SOUTH_WEST:
                x -= 1
                y += 1
            elif self._direction == WEST:
                x -= 1
            elif self._direction == NORTH_WEST:
                x -= 1
                y -= 1

            self._mobile.position = Position(x, y, oldpos.z, self._direction)
        else:
            self._mobile.position = Position(oldpos.x, oldpos.y, oldpos.z,
                                             self._direction)

        self._seq = None
        self._direction = None
