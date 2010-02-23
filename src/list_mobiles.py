#!/usr/bin/python

from gemuo.simple import SimpleClient

client = SimpleClient()
for x in client.world.mobiles():
    print x
