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

def find_wool(world):
    return world.find_player_item(lambda x: x.item_id == ITEM_WOOL)

def find_reachable_spinning_wheel(world):
    return world.find_reachable_item(lambda x: x.item_id in ITEMS_SPINNING_WHEEL)

class SpinWool(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self.target_mutex = client.target_mutex
        self.spinningwheel = find_reachable_spinning_wheel(client.world)
        print self.spinningwheel
        if self.spinningwheel is None:
            print "No spinningwheel"
            self._failure()
            return
        self._next()

    def _next(self):
        client = self._client
        self.wool = find_wool(client.world)
        if self.wool is None:
            self._success()
            return

        self.target_mutex.get_target(self.target_ok, self.target_abort)

    def target_ok(self):
        client = self._client
        client.send(p.Use(self.wool.serial))

        self.engine = SendTarget(client, Target(serial=self.spinningwheel.serial))
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
    d = defer_engine(client, SpinWool(client))
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
