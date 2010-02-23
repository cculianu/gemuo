#!/usr/bin/python

from gemuo.simple import SimpleClient
from gemuo.engine.items import OpenContainer

client = SimpleClient()
if client.world.backpack() is None:
    raise "No backpack"

oc = OpenContainer(client, client.world.backpack())
client.until(oc.finished)

for x in client.world.items_in(client.world.backpack()):
    print x
