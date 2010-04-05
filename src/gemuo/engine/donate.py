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

from uo.entity import ITEM_GOLD
from gemuo.defer import deferred_find_player_item
from gemuo.engine import Engine
from gemuo.engine.util import Repeat
from gemuo.engine.restock import drop_into

class DonateOnce(Engine):
    def __init__(self, client, to):
        Engine.__init__(self, client)

        self._to = to

        d = deferred_find_player_item(client, lambda x: x.item_id == ITEM_GOLD)
        # No gold is success, because this engine is meant for use
        # cases where you donate all your money to raise Karma
        d.addCallbacks(self._donate, self._success)

    def _donate(self, gold):
        drop_into(self._client, gold, self._to, 1)
        self._success()

def DonateLoop(client, to):
    return Repeat(client, 1, DonateOnce, to)
