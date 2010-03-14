#!/usr/bin/python

from uo.skills import *
from gemuo.simple import SimpleClient
from gemuo.engine.messages import PrintMessages
from gemuo.engine.bandage import CutCloth
from gemuo.engine.items import OpenContainer

client = SimpleClient()
PrintMessages(client)
client.until(OpenContainer(client, client.world.backpack()).finished)
cc = CutCloth(client)
client.until(cc.finished)
