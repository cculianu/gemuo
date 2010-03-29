#!/usr/bin/python

from uo.entity import TREES
from gemuo.simple import simple_run
from gemuo.data import TileCache
from gemuo.entity import Position
from gemuo.exhaust import ExhaustDatabase
from gemuo.resource import find_resource
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.guards import Guards
from gemuo.engine.lumber import Lumber
from gemuo.engine.walk import PathFindWalk

def find_tree(map, exhaust_db, position):
    item_id, x, y, z = find_resource(map, position, TREES, exhaust_db)
    print "tree:", item_id, x, y, z
    return Position(x, y)

class AutoKindling(Engine):
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

        self._walk()

    def _walked(self, result):
        d = Lumber(self._client, self.map, self.tree, self.exhaust_db).deferred
        d.addCallbacks(self._lumbered, self._success)

    def _walk_failed(self, fail):
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
        d = PathFindWalk(self._client, self.map, position).deferred
        d.addCallbacks(self._walked, self._walk_failed)

def run(client):
    PrintMessages(client)
    Guards(client)

    tc = TileCache('/home/max/.wine/drive_c/uo')
    m = tc.get_map(0)
    exhaust_db = ExhaustDatabase('/tmp/trees.db')

    return AutoKindling(client, m, exhaust_db)

simple_run(run)
