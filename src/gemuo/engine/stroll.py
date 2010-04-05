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

import random
from twisted.internet import reactor
from gemuo.path import Position
from gemuo.engine import Engine
from gemuo.engine.walk import PathFindWalk

class StrollWestBritain(Engine):
    def __init__(self, client, map):
        Engine.__init__(self, client)

        self.map = map
        self.min_x, self.min_y = 1429,1540
        self.max_x, self.max_y = 1516,1734
        self.random = random.Random()
        self._next_walk()

    def _next_walk(self):
        client = self._client
        to = Position(self.random.randint(self.min_x, self.max_x),
                      self.random.randint(self.min_y, self.max_y))
        d = PathFindWalk(client, self.map, to).deferred
        d.addCallbacks(self._walked, self._walked)

    def _walked(self, result):
        reactor.callLater(2, self._next_walk)
