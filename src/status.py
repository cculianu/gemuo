#!/usr/bin/python

from uo.skills import *
from uo.stats import *
import uo.packets as p
from gemuo.simple import SimpleClient
from gemuo.util import AllFinished
from gemuo.engine.player import QuerySkills, QueryStats

client = SimpleClient()
client.until(AllFinished(QuerySkills(client), QueryStats(client)))

player = client.world.player
print "Name:", "\t", player.name
print "Stats:", "\t", zip(("Str", "Dex", "Int"), player.stats)

print "Skills:"
skills = filter(lambda x: x.base > 0, player.skills.itervalues())
skills.sort(lambda a, b: cmp(a.base, b.base), reverse=True)
total = 0
for x in skills:
    print "\t", SKILL_NAMES[x.id], x.base / 10.0, LOCK_NAMES[x.lock]
    total += x.base
print "\t", "Total", total / 10.0

print "Equipped:"
for x in client.world.items_in(client.world.player):
    print "\t", x
