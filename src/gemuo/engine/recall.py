#
#  GemUO
#
#  (c) 2005-2010 Max Kellermann <max@duempel.org>
#                Kai Sassmannshausen <kai@sassie.org>
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
from gemuo.engine.items import OpenContainer
from gemuo.target import Target, SendTarget
from uo.spells import SPELL_RECALL
from uo.entity import ITEM_RECALL_RUNE
from twisted.python import log
from gemuo.error import Timeout
from twisted.internet import reactor
import random
import re

class Recall(Engine):
    def __init__(self, client, destination=None):
        Engine.__init__(self, client)
        self.dest = destination
        self.runes = list()
        self.call_id = reactor.callLater(4, self._timeout)
        self.open_backpack()

    def get_runes(self, result, world, container):
        for x in world.items_in(container):
            if x.item_id ==  ITEM_RECALL_RUNE:
                self.runes.append(Rune(x.serial))
                self.request_rune_data(x)

    def request_rune_data(self, rune):
        self._client.send(p.Click(rune.serial))

    def check_rune(self, ascii_message):
        if ascii_message is not None:
            ts = re.split("^a recall rune for ", ascii_message.text)
            desc = ts.pop()
            if self.dest is not None:
                if desc == self.dest:
                    self.recall_at_rune(Rune(ascii_message.serial))
            else:
                self.recall_at_rune(self.runes[self.random_rune()])
                
    def open_backpack(self):
        backpack = self._client.world.backpack()
        if backpack is None:
            return defer.fail('No backpack')
        
        d = OpenContainer(self._client, backpack).deferred
        d.addCallback(self.get_runes, self._client.world, backpack)
        return d

    def random_rune(self):
        if self.runes.count > 0:
            return random.randint(1, len(self.runes)) -1

    def recall_at_rune(self, rune):
        d = CastTargetSpell(self._client, SPELL_RECALL, rune).deferred
        
    def on_packet(self, packet):
        if isinstance(packet, p.MobileUpdate):
            if packet.serial == self._client.world.player.serial:
                log.msg("Recalled to %d / %d / %d" % ( packet.x, packet.y, packet.z ))
                self.call_id.cancel()
                self._success()
        elif isinstance(packet, p.AsciiMessage):
            self.check_rune(packet)

    def _timeout(self):
        self._failure(Timeout("Recall timeout"))

class CastTargetSpell(Engine):
    def __init__(self, client, spell, target):
        Engine.__init__(self, client)

        self.spell = spell
        self.target = target

        self.target_mutex = client.target_mutex
        self.target_mutex.get_target(self._target_ok, self._target_abort)

    def _target_ok(self):
        self._client.send(p.Cast(self.spell))
        self.engine = SendTarget(self._client, Target(self.target.serial))
        self.engine.deferred.addCallbacks(self._target_sent, self._target_failed)

    def _target_abort(self):
        self.engine.abort()
        self._failure()

    def _target_sent(self, result):
        self.target_mutex.put_target()
        reactor.callLater(2, self._success)

    def _target_failed(self, fail):
        self.target_mutex.put_target()
        self._failure(fail)

class Rune():
    
    def __init__(self, serial):
        self.serial = serial
        self.description = None
