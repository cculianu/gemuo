#!/usr/bin/python

from uo.entity import *
from gemuo.simple import simple_run
from gemuo.defer import deferred_find_item_in_backpack
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.items import UseAndTarget
from gemuo.engine.util import DelayedCallback
from gemuo.engine.hide import AutoHide

def find_reachable_spinning_wheel(world):
    return world.find_reachable_item(lambda x: x.item_id in ITEMS_SPINNING_WHEEL)

class SpinWool(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self.spinningwheel = find_reachable_spinning_wheel(client.world)
        print self.spinningwheel
        if self.spinningwheel is None:
            print "No spinningwheel"
            self._failure()
            return
        self._next()

    def _next(self):
        d = deferred_find_item_in_backpack(self._client, lambda x: x.item_id == ITEM_WOOL)
        d.addCallbacks(self._found_wool, self._success)

    def _found_wool(self, wool):
        d = UseAndTarget(self._client, wool, self.spinningwheel).deferred
        d.addCallbacks(self._done, self._failure)

    def _done(self, result):
        DelayedCallback(self._client, 3.5, self._next)

def run(client):
    PrintMessages(client)
    AutoHide(client)

    return SpinWool(client)

simple_run(run)
