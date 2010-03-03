#!/usr/bin/python

from uo.skills import *
from gemuo.simple import SimpleClient
from gemuo.engine.messages import PrintMessages
from gemuo.engine.bandage import CutCloth

client = SimpleClient()
PrintMessages(client)
cc = CutCloth(client)
client.until(cc.finished)
