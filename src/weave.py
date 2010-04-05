#!/usr/bin/python

from twisted.internet import reactor
from uo.entity import *
from gemuo.simple import simple_run
from gemuo.defer import deferred_find_item_in_backpack
from gemuo.error import *
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.items import UseAndTarget
from gemuo.engine.hide import AutoHide

def find_reachable_loom(world):
    return world.find_reachable_item(lambda x: x.item_id in ITEMS_LOOM)

class WeaveYarn(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self.target_mutex = client.target_mutex
        self.loom = find_reachable_loom(client.world)
        if self.loom is None:
            self._failure(NoSuchEntity('No loom'))
            return

        self._next()

    def _next(self):
        d = deferred_find_item_in_backpack(self._client, lambda x: x.item_id in ITEMS_YARN and x.amount >= 5)
        d.addCallbacks(self._found_yarn, self._success)

    def _found_yarn(self, yarn):
        d = UseAndTarget(self._client, yarn, self.loom).deferred
        d.addCallbacks(self._done, self._failure)

    def _done(self, result):
        reactor.callLater(3.5, self._next)

def run(client):
    PrintMessages(client)
    AutoHide(client)

    return WeaveYarn(client)

simple_run(run)
