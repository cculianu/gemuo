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

import uo.packets as p
from gemuo.engine import Engine

class QuerySkills(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        self.skills = None
        client.send(p.MobileQuery(0x05, client.world.player.serial))

    def abort(self):
        self._failure()

    def on_skill_update(self, skills):
        self.skills = skills
        self._success()

class QueryStats(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        self.stats = None
        client.send(p.MobileQuery(0x04, client.world.player.serial))

    def abort(self):
        self._failure()

    def on_mobile_status(self, mobile):
        player = self._client.world.player
        if mobile == player:
            self.stats = player.stats
            if self.stats is not None:
                self._success()
            else:
                self._failure()
