#
#  GemUO
#
#  (c) 2005-2010 Max Kellermann <max@duempel.org>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 2 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#

from sys import argv, stderr, exit
import logging
from twisted.python import log
from twisted.internet import reactor, defer
from twisted.internet.interfaces import IDelayedCall
from gemuo.client import login, connect
from gemuo.engine.login import Login
from gemuo.world import World
from gemuo.translate import Translate
from gemuo.target import TargetMutex
from gemuo.engine import Engine

observer = log.PythonLoggingObserver()
observer.start()

logger = logging.getLogger(None)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stderr)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class SimpleClientWrapper:
    def __init__(self, client):
        self.client = client
        self.world = World(client)
        self.translate = Translate(client)
        self.target_mutex = TargetMutex()

    def __getattr__(self, name):
        x = getattr(self.client, name)
        setattr(self, name, x)
        return x

def simple_connect(*args, **keywords):
    d = defer.Deferred()

    e = connect(*args, **keywords)
    e.addCallback(lambda client: d.callback(SimpleClientWrapper(client)))
    e.addErrback(lambda f: d.errback(f))

    return d

def simple_login():
    if len(argv) != 6:
        print >>stderr, "Usage: %s host port username password charname"
        exit(1)

    host, port, username, password, character = argv[1:]
    port = int(port)

    return login(host, port, username, password, character, connect=simple_connect)

def simple_callback(result):
    if result is None:
        reactor.stop()
    elif IDelayedCall.implementedBy(result.__class__):
        pass
    elif isinstance(result, Engine):
        d = result.deferred
        d.addCallback(simple_callback)
        d.addErrback(simple_err)
    else:
        result.addCallback(simple_callback)
        result.addErrback(simple_err)

def simple_later(delay, func, *args, **keywords):
    def cb():
        simple_callback(func(*args, **keywords))
    return reactor.callLater(delay, cb)

def simple_err(fail):
    fail.printTraceback()
    reactor.stop()

def simple_run(run):
    d = simple_login()
    d.addCallback(run)
    d.addCallback(simple_callback)
    d.addErrback(simple_err)
    reactor.run()
