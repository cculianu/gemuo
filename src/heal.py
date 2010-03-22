#!/usr/bin/python

from gemuo.simple import SimpleClient
from gemuo.engine.messages import PrintMessages
from gemuo.engine.watch import Watch
from gemuo.engine.heal import AutoHeal
from gemuo.engine.trade import AutoCheckSecureTrade

client = SimpleClient()
PrintMessages(client)
Watch(client)
AutoCheckSecureTrade(client)
client.until(AutoHeal(client).finished)
