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

from twisted.internet import reactor
import uo.packets as p
from uo.entity import TREES
from gemuo.engine import Engine
from gemuo.target import Target
from gemuo.engine.items import UseAndTarget

def find_axe(world):
    return world.equipped_item(world.player, 0x2) or world.equipped_item(world.player, 0x1)

def is_tree(item_id):
    return ((item_id & 0x3fff) | 0x4000) in TREES

def find_tree(map, position):
    for id, z, hue in map.statics_at(position.x, position.y):
        if is_tree(id):
            return Target(x=position.x, y=position.y, z=z, graphic=id)
    return None

class Lumber(Engine):
    def __init__(self, client, map, tree, exhaust_db):
        Engine.__init__(self, client)

        self.exhaust_db = exhaust_db
        self.exhausted = False
        self.tries = 5

        self.axe = find_axe(client.world)
        if self.axe is None:
            self._failure('No axe')
            return

        self.tree = find_tree(map, tree)
        if self.tree is None:
            self._failure('No tree at %s' % tree)
            return

        self._begin_chop()

    def _begin_chop(self):
        player = self._client.world.player
        if player.mass_remaining() < 40:
            self._success()
            return

        d = UseAndTarget(self._client, self.axe, self.tree).deferred
        d.addCallbacks(self._chopped, self._target_failure)

    def _target_failure(self, fail):
        self.tries -= 1
        if self.tries > 0:
            self._begin_chop()
        else:
            self._failure(fail)

    def _chopped(self, result):
        self.tries = 5
        if self.exhausted:
            self._success()
        else:
            reactor.callLater(1, self._begin_chop)

    def on_packet(self, packet):
        if isinstance(packet, p.AsciiMessage):
            if packet.type == 0 and packet.serial == 0xffffffff and \
               packet.name == 'System' and 'not enough wood here' in packet.text:
                self.exhausted = True
                self.exhaust_db.set_exhausted(self.tree.x / 8, self.tree.y / 8)
