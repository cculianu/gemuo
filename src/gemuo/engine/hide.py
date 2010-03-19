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
from uo.skills import SKILL_HIDING
import uo.packets as p
import uo.rules
from gemuo.engine import Engine
from gemuo.timer import TimerEvent

class AutoHide(Engine, TimerEvent):
    def __init__(self, client):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self.scheduled = False
        self.update(client.world.player)

    def update(self, player):
        if not self.scheduled and not player.is_hidden():
            client = self._client
            client.send(p.UseSkill(SKILL_HIDING))
            self.scheduled = True
            self._schedule(uo.rules.skill_delay(SKILL_HIDING))

    def on_mobile_update(self, mobile):
        client = self._client
        if mobile == client.world.player:
            self.update(mobile)

    def tick(self):
        self.scheduled = False
        client = self._client
        self.update(client.world.player)
