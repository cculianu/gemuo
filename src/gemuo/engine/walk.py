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

from uo.entity import *
import uo.packets as p
from uo.entity import SERIAL_PLAYER
from gemuo.engine import Engine

class WalkPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(%d,%d)" % (self.x, self.y)

class DirectWalk(Engine):
    def __init__(self, client, destination):
        Engine.__init__(self, client)

        self.player = client.world.player
        self.walk = client.world.walk
        self.destination = destination

        self._next_walk()

    def _distance2(self, position):
        player = self.player.position
        dx = player.x - position.x
        dy = player.y - position.y
        return dx*dx + dy*dy

    def _direction_from(self, position):
        destination = self.destination
        if destination.x < position.x:
            if destination.y < position.y:
                return NORTH_WEST
            elif destination.y > position.y:
                return SOUTH_WEST
            else:
                return WEST
        elif destination.x > position.x:
            if destination.y < position.y:
                return NORTH_EAST
            elif destination.y > position.y:
                return SOUTH_EAST
            else:
                return EAST
        else:
            if destination.y < position.y:
                return NORTH
            elif destination.y > position.y:
                return SOUTH
            else:
                return None

    def _next_walk(self):
        player = self.player
        position = player.position
        if position is None:
            self._failure()

        direction = self._direction_from(position)
        if direction is None:
            self._success()
            return

        if player.stamina is not None and player.stamina.value > 20 and self._distance2(position) >= 4:
            direction |= RUNNING

        self._client.send(self.walk.walk(direction))

    def on_walk_reject(self):
        self._failure()

    def on_walk_ack(self):
        self._next_walk()

class PathWalk(Engine):
    def __init__(self, client, path):
        Engine.__init__(self, client)

        self.player = client.world.player
        self.path = list(path)
        self.walk = None

        self._next_walk()

    def _distance2(self, position):
        player = self.player.position
        dx = player.x - position.x
        dy = player.y - position.y
        return dx*dx + dy*dy

    def _next_walk(self):
        # find nearest point
        nearest = None
        nearest_distance2 = 999999

        for x in self.path:
            distance2 = self._distance2(x)
            if distance2 < nearest_distance2:
                nearest = x
                nearest_distance2 = distance2

        if nearest is None:
            print "done"
            self._success()

        while self.path[0] != nearest:
            self.path = self.path[1:]

        if nearest_distance2 == 0:
            self.path = self.path[1:]
            self._next_walk()
            return

        print "Walk to", nearest, nearest_distance2
        self.walk = DirectWalk(self._client, nearest)

    def on_engine_success(self, engine, *args, **keywords):
        if engine == self.walk:
            self.walk = None
            self.path = self.path[1:]
            self._next_walk()

    def on_engine_failure(self, engine, *args, **keywords):
        if engine == self.walk:
            print "Walk failed"
            self.walk = None
            self._next_walk()
