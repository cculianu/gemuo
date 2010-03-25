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
        self.yarn = find_yarn(client.world)
        if self.yarn is None or self.yarn.amount < 5:
            self._success()
            return

        self.target_mutex.get_target(self.target_ok, self.target_abort)

    def target_ok(self):
        client = self._client
        client.send(p.Use(self.yarn.serial))

        self.engine = SendTarget(client, Target(serial=self.loom.serial))
        FinishCallback(client, self.engine, self._target_sent)

    def target_abort(self):
        self.engine.abort()
        self._failure()

    def _target_sent(self, success):
        self.target_mutex.put_target()

        if success:
            DelayedCallback(self._client, 3.5, self._next)
        else:
            self._failure()


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
