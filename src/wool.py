#!/usr/bin/python

from twisted.internet import reactor, defer
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
from gemuo.engine.hide import AutoHide
from gemuo.engine.restock import Restock

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
        d = self.engine.deferred
        d.addCallbacks(self._target_sent, self._target_failed)

    def target_abort(self):
        self.engine.abort()
        self._failure()

    def _target_sent(self, result):
        client = self._client
        self.engine = SendTarget(self._client, Target(serial=client.world.player.serial))
        d = self.engine.deferred
        d.addCallbacks(self._player_sent, self._target_failed)

    def _player_sent(self, result):
        self.target_mutex.put_target()
        reactor.callLater(1, self._next)

    def _target_failed(self, fail):
        self.target_mutex.put_target()
        self._failure(fail)

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
            d = HerdSheep(client).deferred
            d.addCallbacks(self._herded, self._failure)
            return

        dagger = find_dagger(client.world)
        if dagger is None:
            print "No dagger"
            self._failure()
            return

        d = UseAndTarget(client, dagger, sheep).deferred
        d.addCallbacks(self._harvested, self._failure)

    def _herded(self, result):
        reactor.callLater(4, self._next)

    def _harvested(self, result):
        reactor.callLater(1, self._next)

def chest_opened(client, chest):
    return Restock(client, chest, func=lambda x: x.item_id == ITEM_WOOL)

def chest_opened0(result, *args, **keywords):
    return simple_later(1, chest_opened, *args, **keywords)

def harvested(result, client):
    chest = find_chest_at(client.world, client.world.player.position.x - 2,
                          client.world.player.position.y)
    if chest is None:
        return defer.fail('No chest')

    d = OpenContainer(client, chest).deferred
    d.addCallback(chest_opened0, client, chest)
    return d

def backpack_opened(client):
    d = HarvestWool(client).deferred
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

    d = OpenContainer(client, backpack).deferred
    d.addCallback(backpack_opened0, client)
    return d

simple_run(run)
