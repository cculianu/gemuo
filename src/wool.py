#!/usr/bin/python

from twisted.internet import defer
import uo.packets as p
from uo.skills import *
from uo.entity import *
from gemuo.simple import simple_run, simple_later
from gemuo.target import Target, SendTarget
from gemuo.entity import Item
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.watch import Watch
from gemuo.engine.items import OpenContainer, UseAndTarget
from gemuo.engine.util import FinishCallback, Delayed, DelayedCallback
from gemuo.engine.hide import AutoHide
from gemuo.engine.restock import Restock
from gemuo.engine.defer import defer_engine

def find_crook(world):
    return world.find_player_item(lambda x: x.item_id == ITEM_CROOK)

def find_dagger(world):
    return world.find_player_item(lambda x: x.item_id == ITEM_DAGGER)

def find_sheep(world):
    return filter(lambda x: x.body == CREATURE_SHEEP, world.iter_mobiles())

def find_reachable_sheep(world):
    return world.find_reachable_mobile(lambda x: x.body == CREATURE_SHEEP)

def find_chest_at(world, x, y):
    for e in world.iter_entities_at(x, y):
        if isinstance(e, Item) and e.item_id in ITEMS_CHEST:
            return e
    return None

class HerdSheep(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self.target_mutex = client.target_mutex
        self.sheep = find_sheep(client.world)
        self._next()

    def _next(self):
        if len(self.sheep) == 0:
            self._success()
            return

        client = self._client
        self.crook = find_crook(client.world)
        if self.crook is None:
            print "No crook"
            self._failure()
            return

        self.target, self.sheep = self.sheep[0], self.sheep[1:]

        self.target_mutex.get_target(self.target_ok, self.target_abort)

    def target_ok(self):
        client = self._client
        client.send(p.Use(self.crook.serial))

        self.engine = SendTarget(client, Target(serial=self.target.serial))
        FinishCallback(client, self.engine, self._target_sent)

    def target_abort(self):
        self.engine.abort()
        self._failure()

    def _target_sent(self, success):
        if not success:
            self.target_mutex.put_target()
            self._failure()
            return

        client = self._client
        self.engine = SendTarget(client, Target(serial=client.world.player.serial))
        FinishCallback(client, self.engine, self._player_sent)

    def _player_sent(self, success):
        self.target_mutex.put_target()

        if success:
            DelayedCallback(self._client, 1, self._next)
        else:
            self._failure()

class HarvestWool(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self._next()

    def _next(self):
        client = self._client

        sheep = find_sheep(client.world)
        if len(sheep) == 0:
            self._success()
            return

        sheep = find_reachable_sheep(client.world)
        if sheep is None:
            FinishCallback(client, HerdSheep(client), self._herded)
            return

        dagger = find_dagger(client.world)
        if dagger is None:
            print "No dagger"
            self._failure()
            return

        FinishCallback(client, UseAndTarget(client, dagger, sheep), self._harvested)

    def _herded(self, success):
        if not success:
            self._failure()
            return

        DelayedCallback(self._client, 4, self._next)

    def _harvested(self, success):
        if not success:
            self._failure()
            return

        DelayedCallback(self._client, 1, self._next)

def chest_opened(client, chest):
    return Restock(client, chest, func=lambda x: x.item_id == ITEM_WOOL)

def chest_opened0(result, *args, **keywords):
    return simple_later(1, chest_opened, *args, **keywords)

def harvested(result, client):
    chest = find_chest_at(client.world, client.world.player.position.x - 2,
                          client.world.player.position.y)
    if chest is None:
        return defer.fail('No chest')

    d = defer_engine(client, OpenContainer(client, chest))
    d.addCallback(chest_opened0, client, chest)
    return d

def backpack_opened(client):
    d = defer_engine(client, HarvestWool(client))
    d.addCallback(harvested, client)
    return d

def backpack_opened0(result, *args, **keywords):
    return simple_later(1, backpack_opened, *args, **keywords)

def run(client):
    PrintMessages(client)
    AutoHide(client)

    backpack = client.world.backpack()
    if backpack is None:
        return defer.fail('No backpack')

    d = defer_engine(client, OpenContainer(client, backpack))
    d.addCallback(backpack_opened0, client)
    return d

simple_run(run)
