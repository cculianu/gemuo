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

from twisted.python.failure import Failure
from twisted.internet import reactor, defer
from gemuo.engine.items import OpenContainer
from gemuo.engine.player import QuerySkills

def deferred_find_item_in(client, parent, func):
    i = client.world.find_item_in(parent, func)
    if i is not None:
        return defer.succeed(i)

    d = defer.Deferred()
    e = OpenContainer(client, parent).deferred

    def second_lookup():
        i = client.world.find_item_in(parent, func)
        if i is not None:
            d.callback(i)
        else:
            d.errback('No such item')

    def callback(result):
        reactor.callLater(1, second_lookup)
        return result

    def errback(fail):
        d.errback(fail)
        return fail

    e.addCallbacks(callback, errback)
    return d

def deferred_find_item_in_backpack(client, func):
    backpack = client.world.backpack()
    if backpack is None:
        return defer.fail('No backpack')

    return deferred_find_item_in(client, backpack, func)

def deferred_nearest_reachable_item(client, func):
    i = client.world.nearest_reachable_item(func)
    if i is not None:
        return defer.succeed(i)

    return deferred_find_item_in_backpack(client, func)

def deferred_find_player_item(client, func):
    i = client.world.find_player_item(func)
    if i is not None:
        return defer.succeed(i)

    return deferred_find_item_in_backpack(client, func)

def deferred_skills(client):
    skills = client.world.player.skills
    if skills is not None:
        return defer.succeed(skills)

    d = defer.Deferred()
    e = QuerySkills(client).deferred

    def callback(result):
        skills = client.world.player.skills
        if skills is not None:
            d.callback(skills)
        else:
            defer.errback('No skill info available')
        return result

    def errback(fail):
        d.errback(fail)
        return fail

    e.addCallbacks(callback, errback)
    return d

def deferred_skill(client, skill):
    d = defer.Deferred()
    e = deferred_skills(client)

    def callback(result):
        if skill in result:
            d.callback(result[skill])
        else:
            defer.errback('Skill not found')
        return result

    def errback(fail):
        d.errback(fail)
        return fail

    e.addCallbacks(callback, errback)
    return d
