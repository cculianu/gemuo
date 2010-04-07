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

from random import Random
from twisted.internet import reactor
from uo.entity import *
from gemuo.entity import Item
from gemuo.simple import simple_run, simple_later
from gemuo.data import TileCache
from gemuo.entity import Position
from gemuo.exhaust import ExhaustDatabase
from gemuo.resource import find_resource
from gemuo.defer import deferred_find_player_item
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.guards import Guards
from gemuo.engine.equip import Equip
from gemuo.engine.lumber import Lumber
from gemuo.engine.walk import PathFindWalk
from gemuo.engine.watch import Watch
from gemuo.engine.items import OpenBank
from gemuo.engine.restock import Restock
from gemuo.engine.gm import DetectGameMaster

BANK = None

BRITAIN_EAST_BANK = (1646,1598, 1646,1616, 1720,1580)
MINOC_BANK = (2493,541, 2513,561, 2500,570)
MOONGLOW_BANK = (4461,1150, 4481,1176, 4442,1200)

random = Random()

def PathFindWalkRectangle(client, map, rectangle):
    assert rectangle[0] <= rectangle[2]
    assert rectangle[1] <= rectangle[3]

    wx = rectangle[2] - rectangle[0]
    wy = rectangle[3] - rectangle[1]

    player = client.world.player.position
    x, y = player.x + random.randint(-8, 8), player.y + random.randint(-8, 8)
    x += random.randint(-wx / 2, wx / 2)
    y += random.randint(-wy / 2, wy / 2)

    if x < rectangle[0]:
        x = rectangle[0]
    elif x > rectangle[2]:
        x = rectangle[2]

    if y < rectangle[1]:
        y = rectangle[1]
    elif y > rectangle[3]:
        y = rectangle[3]

    return PathFindWalk(client, map, Position(x, y))

def find_tree(map, exhaust_db, position):
    center = Position((position.x * 7 + BANK[4]) / 8,
                      (position.y * 7 + BANK[5]) / 8)
    item_id, x, y, z = find_resource(map, center, TREES, exhaust_db)
    print "tree:", x, y, z
    return Position(x, y)

class AutoLumber(Engine):
    def __init__(self, client, map, exhaust_db):
        Engine.__init__(self, client)
        self.player = client.world.player
        self.map = map
        self.exhaust_db = exhaust_db

        if self.player.mass_remaining() < 50:
            self._success()
            return

        self._walk()

    def _lumbered(self, result):
        if self.player.mass_remaining() < 50:
            # too heavy, finish this engine
            self._success()
            return

        reactor.callLater(0.5, self._walk)

    def _equipped(self, result):
        d = Lumber(self._client, self.map, self.tree, self.exhaust_db).deferred
        d.addCallbacks(self._lumbered, self._success)

    def _walked(self, result):
        # make sure an axe is equipped
        d = Equip(self._client, lambda x: x.item_id in ITEMS_AXE).deferred
        d.addCallbacks(self._equipped, self._failure)

    def _walk_failed(self, fail):
        # walking to this tree failed for some reason; mark this 8x8
        # as "exhausted", so we won't try it again for a while
        self.exhaust_db.set_exhausted(self.tree.x/8, self.tree.y/8)
        self._walk()

    def _walk(self):
        position = self.player.position
        if position is None:
            self._failure()
            return

        self.tree = find_tree(self.map, self.exhaust_db, position)
        if self.tree is None:
            self._failure()
            return

        x, y = self.tree.x, self.tree.y
        if position.x < self.tree.x:
            x -= 1
        elif position.x > self.tree.x:
            x += 1
        if position.y < self.tree.y:
            y -= 1
        elif position.y > self.tree.y:
            y += 1

        position = Position(x, y)
        client = self._client
        d = PathFindWalk(self._client, self.map, position).deferred
        d.addCallbacks(self._walked, self._walk_failed)

class Bank(Engine):
    def __init__(self, client, map):
        Engine.__init__(self, client)
        self._map = map
        self.tries = 5

        print "Bank"
        self._walk()

    def _walk(self):
        d = PathFindWalkRectangle(self._client, self._map, BANK).deferred
        d.addCallbacks(self._walked, self._walk_failed)

    def _walk_failed(self, fail):
        self.tries -= 1
        if self.tries > 0:
            self._walk()
        else:
            self._failure(fail)

    def _walked(self, result):
        d = OpenBank(self._client).deferred
        d.addCallbacks(self._opened, self._walk_failed)

    def _out_filter(self, x):
        return x.item_id not in ITEMS_AXE

    def _opened(self, bank):
        d = Restock(self._client, bank, func=self._out_filter,
                    counts=((ITEMS_AXE, 1),)).deferred
        d.addCallbacks(self._restocked, self._failure)

    def _restocked(self, result):
        self._success()

class AutoHarvest(Engine):
    def __init__(self, client, map, exhaust_db):
        Engine.__init__(self, client)
        self.player = client.world.player
        self.map = map
        self.exhaust_db = exhaust_db

        self._check()

    def _restocked(self, result):
        self._begin_lumber()

    def _restock(self):
        d = Bank(self._client, self.map).deferred
        d.addCallbacks(self._restocked, self._failure)

    def _found_axe(self, axe):
        self._begin_lumber()

    def _no_axe(self, fail):
        self._restock()

    def _check(self):
        if self.player.mass_remaining() < 50:
            self._restock()
        else:
            d = deferred_find_player_item(self._client, lambda x: x.item_id in ITEMS_AXE)
            d.addCallbacks(self._found_axe, self._no_axe)

    def _lumbered(self, result):
        self._check()

    def _begin_lumber(self):
        d = AutoLumber(self._client, self.map, self.exhaust_db).deferred
        d.addCallbacks(self._lumbered, self._failure)

class BridgeMap:
    """A wrapper for the map class which allows PathFindWalk to walk
    over bridges.  We havn't implemented walking over statics properly
    yet, but this hack is good enough for now."""

    def __init__(self, map, client):
        self.map = map
        self.client = client
        self.statics = map.statics

    def is_passable(self, x, y, z):
        client = self.client
        world = client.world
        for e in world.iter_entities_at(x, y):
            if isinstance(e, Item):
                if e.item_id in (0x1BC3, # teleporter
                                 0xF6C, # moongate
                                 ):
                    # don't step through moongates
                    return False
                if not self.map.tile_data.item_passable(e.item_id & 0x3fff):
                    return False
            else:
                if e.serial != world.player.serial:
                    # never step over other mobiles
                    return False

        if x >= 1376 and x <= 1398 and y >= 1745 and y <= 1753: return True
        if x >= 1517 and x <= 1530 and y >= 1671 and y <= 1674: return True
        if x >= 2528 and x <= 2550 and y >= 499 and y <= 502: return True
        if x >= 2528 and x <= 2550 and y >= 499 and y <= 502: return True

        # brit mauer
        if x >= 1419 and x <= 1421 and y >= 1633 and y <= 1638: return True
        if x >= 1462 and x <= 1466 and y >= 1639 and y <= 1643: return True
        if x >= 1468 and x <= 1472 and y >= 1639 and y <= 1643: return True
        if x >= 1478 and x <= 1482 and y >= 1639 and y <= 1643: return True
        if x >= 1480 and x <= 1484 and y >= 1639 and y <= 1643: return True

        return self.map.is_passable(x, y, z)

    def __getattr__(self, name):
        x = getattr(self.map, name)
        setattr(self, name, x)
        return x

def begin(client):
    from os import environ
    tc = TileCache('%s/.wine/drive_c/uo' % environ['HOME'])
    m = BridgeMap(tc.get_map(0), client)
    exhaust_db = ExhaustDatabase('/tmp/trees.db')

    global BANK
    if client.world.player.position.x < 1500:
        #BANK = BRITAIN_WEST_BANK
        # XXX implement
        pass
    elif client.world.player.position.x < 2000:
        BANK = BRITAIN_EAST_BANK
    elif client.world.player.position.x > 3500:
        BANK = MOONGLOW_BANK
    else:
        BANK = MINOC_BANK
    print client.world.player.position, BANK

    #return Bank(client, m)
    return AutoHarvest(client, m, exhaust_db)

def run(client):
    Watch(client)
    Guards(client)
    DetectGameMaster(client)
    PrintMessages(client)

    return simple_later(1, begin, client)

simple_run(run)
