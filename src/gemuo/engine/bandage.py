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
from gemuo.target import Target, SendTarget
from gemuo.defer import deferred_nearest_reachable_item, deferred_find_item_in_backpack
from gemuo.engine.items import UseAndTarget
from gemuo.engine.util import FinishCallback, DelayedCallback

class CutCloth(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        d = deferred_find_item_in_backpack(client,
                                           lambda x: x.item_id in (0xf9b, 0x1766))
        d.addCallbacks(self._found_cloth, self._success)

    def _found_cloth(self, result):
        self.cloth = result

        client = self._client
        d = deferred_nearest_reachable_item(client,
                                            lambda x: x.item_id in (0xf9e, 0xf9f))
        d.addCallbacks(self._found_scissors, self._failure)

    def _found_scissors(self, result):
        client = self._client
        FinishCallback(client, UseAndTarget(client, result, self.cloth),
                       self._cutted)

    def _cutted(self, success):
        if success:
            DelayedCallback(self._client, 1, self._success)
        else:
            self._failure()

class CutAllCloth(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self._next()

    def _next(self):
        client = self._client
        d = deferred_find_item_in_backpack(client,
                                           lambda x: x.item_id in (0xf9b, 0x1766))
        d.addCallbacks(self._found_cloth, self._success)

    def _found_cloth(self, result):
        client = self._client
        FinishCallback(client, CutCloth(client), self._cutted)

    def _cutted(self, success):
        if success:
            self._next()
        else:
            self._failure()
