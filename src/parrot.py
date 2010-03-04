#!/usr/bin/python

from gemuo.simple import SimpleClient
from gemuo.engine.messages import PrintMessages, Parrot
from gemuo.engine.guards import Guards

client = SimpleClient()
PrintMessages(client)
Guards(client)
client.until(Parrot(client).finished)
