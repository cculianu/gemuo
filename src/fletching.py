#!/usr/bin/python
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
from uo.entity import TREES, ITEMS_AXE
from gemuo.simple import SimpleClient
from gemuo.data import TileCache
from gemuo.entity import Position, Item
from gemuo.exhaust import ExhaustDatabase
from gemuo.resource import find_resource
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.guards import Guards
from gemuo.engine.equip import Equip
from gemuo.engine.watch import Watch
from gemuo.engine.lumber import Lumber
from gemuo.engine.walk import PathFindWalk
from gemuo.engine.util import FinishCallback, DelayedCallback
from gemuo.engine.items import OpenBank
from gemuo.engine.restock import Restock, Trash
from gemuo.engine.fletching import TrainFletching

def amount_in(world, parent, func):
    amount = 0
    for x in world.items_in(parent):
        if func(x):
            amount += x.amount
    return amount

class FletchingRestock(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        world = client.world

        if amount_in(world, world.backpack(), lambda x: x.item_id in (ITEMS_LOGS + ITEMS_BOARDS)) >= 20:
            self._success()
            return

        FinishCallback(client, OpenBank(client), self._box_opened)

    def _box_opened(self, success):
        if not success:
            self._failure()
            return

        bank = self._client.world.bank()
        if bank is None:
            print "No bank"
            self._failure()
            return

        counts = (
            (ITEMS_LOGS + ITEMS_BOARDS, 150),
        )

        client = self._client
        FinishCallback(client, Restock(client, bank, counts=counts),
                       self._restocked)

    def _restocked(self, success):
        if not success:
            self._failure()
            return

        self._success()

class AutoFletching(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        self._trash()

    def _trash(self):
        client = self._client

        FinishCallback(client, Trash(client, ITEMS_FLETCHING_PRODUCTS), self._trashed)

    def _trashed(self, success):
        if not success:
            self._failure()
            return

        client = self._client
        FinishCallback(client, FletchingRestock(client), self._restocked)

    def _restocked(self, success):
        if not success:
            self._failure()
            return

        DelayedCallback(self._client, 1, self._restocked2)

    def _restocked2(self):
        FinishCallback(client, TrainFletching(self._client), self._crafted)

    def _crafted(self, success):
        if not success:
            self._failure()
            return

        self._trash()

client = SimpleClient()

PrintMessages(client)
Guards(client)
Watch(client)
client.until(AutoFletching(client).finished)
