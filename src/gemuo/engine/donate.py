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

from gemuo.engine import Engine
from gemuo.engine.util import FinishCallback, Repeat
from gemuo.engine.items import OpenContainer
from gemuo.engine.restock import drop_into

class DonateOnce(Engine):
    def __init__(self, client, to):
        Engine.__init__(self, client)

        self._to = to
        self._source = client.world.backpack()
        if self._source is None:
            print "No backpack"
            self._failure()
            return

        FinishCallback(client, OpenContainer(client, self._source),
                       self._source_opened)

    def _source_opened(self, success):
        if not success:
            self._failure()
            return

        client = self._client
        world = client.world
        gold = world.find_item_in(self._source, lambda x: x.item_id == 0xeed)
        if gold is None:
            # No gold is success, because this engine is meant for use
            # cases where you donate all your money to raise Karma
            self._success()
            return

        drop_into(client, gold, self._to, 1)
        self._success()

def DonateLoop(client, to):
    return Repeat(client, 1, DonateOnce, to)
