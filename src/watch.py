#!/usr/bin/python

from gemuo.simple import SimpleClient
from gemuo.engine.watch import Watch

client = SimpleClient()
client.until(Watch(client).finished)
