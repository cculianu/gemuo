#!/usr/bin/python

from twisted.internet import defer
from gemuo.simple import simple_run
from gemuo.engine.items import OpenContainer

def print_contents(result, world, container):
    for x in world.items_in(container):
        print x

def run(client):
    backpack = client.world.backpack()
    if backpack is None:
        return defer.fail('No backpack')

    d = OpenContainer(client, backpack).deferred
    d.addCallback(print_contents, client.world, backpack)
    return d

simple_run(run)
