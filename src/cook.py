#!/usr/bin/python

from twisted.internet import reactor
from uo.entity import *
import uo.packets as p
from gemuo.simple import simple_run
from gemuo.error import *
from gemuo.defer import deferred_find_item_in_backpack
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.watch import Watch
from gemuo.engine.items import UseAndTarget
from gemuo.engine.hide import AutoHide

def find_reachable_oven(world):
    return world.find_reachable_item(lambda x: x.item_id in ITEMS_OVEN)

class CookAllFishSteaks(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self.oven = find_reachable_oven(client.world)
        if self.oven is None:
            self._failure(NoSuchEntity('No oven'))
            return

        self._cook_single_steak()

    def _cook_single_steak(self):
        world = self._client.world
        steak = world.find_reachable_item(lambda x: x.item_id == ITEM_RAW_FISH_STEAK and x.amount == 1)
        if steak is None:
            self._unstack()
            return

        d = UseAndTarget(self._client, steak, self.oven).deferred
        d.addCallbacks(self._cooked, self._failure)

    def _cooked(self, result):
        reactor.callLater(5, self._cook_single_steak)

    def _unstack(self):
        client = self._client
        world = client.world
        stack = world.find_reachable_item(lambda x: x.item_id == ITEM_RAW_FISH_STEAK and x.amount >= 2)
        if stack is None:
            self._success()
            return

        client.send(p.LiftRequest(stack.serial, 1))
        client.send(p.Drop(stack.serial, stack.position.x, stack.position.y, stack.position.z, 0))
        reactor.callLater(1, self._cook_single_steak)

def run(client):
    PrintMessages(client)
    Watch(client)
    AutoHide(client)

    return CookAllFishSteaks(client)

simple_run(run)
