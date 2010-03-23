#!/usr/bin/python

from twisted.internet.stdio import StandardIO
from twisted.protocols import basic
from uo.skills import *
from uo.packets import TalkAscii
from gemuo.simple import simple_run
from gemuo.engine import Engine

class Talk(Engine, basic.LineOnlyReceiver):
    delimiter = '\n'
    prompt_string = 'say: '

    def __init__(self, client):
        Engine.__init__(self, client)
        #basic.LineOnlyReceiver.__init__(self)

    def prompt(self):
        self.transport.write(self.prompt_string)

    def connectionMade(self):
        self.prompt()

    def lineReceived(self, line):
        if not line:
            self._success()
            return

        self._client.send(TalkAscii(type=0, hue=0, font=1, text=line))
        self.prompt()

    def connectionLost(self, reason):
        self._success()

def run(client):
    talk = Talk(client)
    StandardIO(talk)
    return talk

simple_run(run)
