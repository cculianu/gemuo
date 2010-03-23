#!/usr/bin/python

from twisted.internet import defer
from uo.skills import *
from gemuo.simple import simple_run, simple_later
from gemuo.engine.messages import PrintMessages
from gemuo.engine.bandage import CutAllCloth
from gemuo.engine.items import OpenContainer
from gemuo.engine.defer import defer_engine

def cut(client):
    return CutAllCloth(client)

def backpack_opened(result, client):
    return simple_later(1, cut, client)

def run(client):
    PrintMessages(client)

    backpack = client.world.backpack()
    if backpack is None:
        return defer.fail('No backpack')

    d = defer_engine(client, OpenContainer(client, backpack))
    d.addCallback(backpack_opened, client)
    return d

simple_run(run)
