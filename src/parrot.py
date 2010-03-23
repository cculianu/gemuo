#!/usr/bin/python

from gemuo.simple import simple_run
from gemuo.engine.messages import PrintMessages, Parrot
from gemuo.engine.guards import Guards

def run(client):
    PrintMessages(client)
    Guards(client)
    return Parrot(client)

simple_run(run)
