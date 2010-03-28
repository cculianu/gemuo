#!/usr/bin/python

from twisted.internet import defer
import uo.packets as p
from uo.skills import *
from uo.entity import *
from gemuo.simple import simple_run, simple_later
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.watch import Watch
from gemuo.engine.items import OpenContainer, UseAndTarget
from gemuo.engine.util import DelayedCallback
from gemuo.engine.hide import AutoHide
from gemuo.engine.restock import Restock
from gemuo.engine.defer import defer_engine

def find_yarn(world):
    return world.find_player_item(lambda x: x.item_id in ITEMS_YARN)

def find_reachable_loom(world):
    return world.find_reachable_item(lambda x: x.item_id in ITEMS_LOOM)

class WeaveYarn(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self.target_mutex = client.target_mutex
        self.loom = find_reachable_loom(client.world)
        if self.loom is None:
            print "No loom"
            self._failure()
            return
        self._next()

    def _next(self):
        client = self._client
        yarn = find_yarn(client.world)
        if yarn is None or yarn.amount < 5:
            self._success()
            return

        d = UseAndTarget(client, yarn, self.loom).deferred
        d.addCallbacks(self._done, self._failure)

    def _done(self, result):
        DelayedCallback(self._client, 3.5, self._next)

def backpack_opened(client):
    d = defer_engine(client, WeaveYarn(client))
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
