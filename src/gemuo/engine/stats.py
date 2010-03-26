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

from uo.stats import *
import uo.packets as p
from gemuo.engine import Engine

class StatLock(Engine):
    """Automatically sets the stack locks to reach the specified goal.
    Leaves all locks to "UP" as long as the sum is below the 225
    cap."""

    def __init__(self, client, goal):
        Engine.__init__(self, client)

        self.player = client.world.player
        self.goal = goal
        self.tries = 10

        if self.player.stat_locks is None:
            # query stats
            client.send(p.MobileQuery(0x04, self.player.serial))

        self._check_stats()

    def _set_lock(self, stat, new_lock):
        if self.player.stat_locks[stat] != new_lock:
            print "Setting stat lock %s to %s" % (STAT_NAMES[stat], LOCK_NAMES[new_lock])
            self._client.send(p.StatLock(stat, new_lock))

    def _check_stats(self):
        if self.player.stats is None or self.player.stat_locks is None:
            print "no stats available"
            self.tries -= 1
            if self.tries > 0:
                self._client.send(p.MobileQuery(0x04, self.player.serial))
            else:
                self._failure()
            return

        cap = self.player.stat_cap or 225
        stats = self.player.stats or (0, 0, 0)
        total = reduce(lambda x,y: x+y, stats)

        if total < cap:
            # below cap: all locks up
            for stat in range(3):
                self._set_lock(stat, LOCK_UP)
            return

        complete = True

        for stat in range(3):
            if stats[stat] > self.goal[stat]:
                self._set_lock(stat, LOCK_DOWN)
                complete = False
            elif stats[stat] < self.goal[stat]:
                self._set_lock(stat, LOCK_UP)
                complete = False
            else:
                self._set_lock(stat, LOCK_LOCKED)

        if complete:
            self._success()

    def on_mobile_status(self, mobile):
        if mobile == self.player:
            self._check_stats()
