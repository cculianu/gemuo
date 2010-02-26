#!/usr/bin/python

import readline
from uo.skills import *
from uo.packets import TalkAscii
from gemuo.simple import SimpleClient

client = SimpleClient()

try:
    while True:
        text = raw_input('say: ')
        client.send(TalkAscii(type=0, hue=0, font=1, text=text))
except EOFError:
    pass
