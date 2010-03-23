#!/usr/bin/python

from gemuo.simple import simple_run
from gemuo.engine.watch import Watch

def run(client):
    return Watch(client)

simple_run(run)
