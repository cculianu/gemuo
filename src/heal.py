#!/usr/bin/python

from gemuo.simple import simple_run
from gemuo.engine.messages import PrintMessages
from gemuo.engine.watch import Watch
from gemuo.engine.heal import AutoHeal
from gemuo.engine.trade import AutoCheckSecureTrade

def run(client):
    PrintMessages(client)
    Watch(client)
    AutoCheckSecureTrade(client)
    return AutoHeal(client)

simple_run(run)
