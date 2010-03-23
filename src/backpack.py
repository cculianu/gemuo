#!/usr/bin/python

from twisted.internet import defer
from gemuo.simple import simple_run
from gemuo.engine.items import OpenContainer
from gemuo.engine.defer import defer_engine

def print_contents(result, world, container):
    for x in world.items_in(container):
        print x

def run(client):
    backpack = client.world.backpack()
    if backpack is None:
        return defer.fail('No backpack')

    d = defer_engine(client, OpenContainer(client, backpack))
    d.addCallback(print_contents, client.world, backpack)
    return d

simple_run(run)
