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
from uo.skills import SKILL_HIDING
import uo.packets as p
import uo.rules
from gemuo.engine import Engine

class AutoHide(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self.call_id = None
        self.update(client.world.player)

    def update(self, player):
        if self.call_id is None and not player.is_hidden():
            client = self._client
            client.send(p.UseSkill(SKILL_HIDING))
            self.call_id = reactor.callLater(uo.rules.skill_delay(SKILL_HIDING),
                                             self._next)

    def on_mobile_update(self, mobile):
        client = self._client
        if mobile == client.world.player:
            self.update(mobile)

    def _next(self):
        self.call_id = None
        client = self._client
        self.update(client.world.player)
