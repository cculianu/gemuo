#!/usr/bin/python
#
#  GemUO
#
#  (c) 2005-2010 Max Kellermann <max@duempel.org>
#                Kai Sassmannshausen <kai@sassie.org>
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

from gemuo.simple import simple_run
from gemuo.engine.recall import Recall
from gemuo.engine.messages import PrintMessages

def run(client):
    PrintMessages(client)

    #recall to a Rune called "Britain"
    #return Recall(client, "Britain")

    #recall to a random rune in the backpack
    return Recall(client)

simple_run(run)
