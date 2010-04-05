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

from twisted.internet import reactor
from uo.skills import *
import uo.packets as p
import uo.rules
from uo.entity import *
from gemuo.defer import deferred_skills
from gemuo.engine import Engine
from gemuo.engine.player import QueryStats
from gemuo.engine.stats import StatLock
from gemuo.engine.training import UseSkill

STAT_SKILLS = (
    (SKILL_ARMS_LORE, SKILL_HERDING),
    (SKILL_MUSICIANSHIP,),
    (SKILL_ITEM_ID, SKILL_EVAL_INT),
)

def select_skill(values, l):
    for x in l:
        if x in values and values[x].base <= 100:
            return x
    return None

class StatJojo(Engine):
    def __init__(self, client, goal):
        Engine.__init__(self, client)

        self.goal = goal

        d = deferred_skills(client)
        d.addCallbacks(self._got_skills, self._failure)

    def _got_skills(self, skills):
        client = self._client

        total = sum(map(lambda x: x.base, skills.itervalues()))
        if total != 7000:
            print "Skill sum is not 700"
            self._failure()
            return

        d = QueryStats(client).deferred
        d.addCallbacks(self._got_stats, self._failure)

    def _got_stats(self, result):
        client = self._client
        player = client.world.player

        if player.stats is None:
            self._failure()
            return

        goal = self.goal
        selected = []
        for i in range(len(player.stats)):
            if player.stats[i] < goal[i]:
                x = select_skill(player.skills, STAT_SKILLS[i])
                if x is not None:
                    selected.append(x)

        if not selected:
            print "No skills selected"
            self._failure()
            return

        selected = selected[:2]
        if len(selected) == 1:
            for x in STAT_SKILLS:
                selected.append(SKILL_ITEM_ID)
                break
                for y in x:
                    if y not in selected and y in player.skills and \
                       player.skills[y].base < 100:
                        selected.append(y)
                        break
                if len(selected) >= 2:
                    break

        d = StatLock(client, goal).deferred
        d.addCallbacks(self._stat_lock_finished, self._failure)

        self.skills = selected
        self._next_skill()

    def _stat_lock_finished(self, result):
        for x in self.skills:
            self._client.send(p.SkillLock(x, SKILL_LOCK_DOWN))

        self._success()

    def _do_skill(self, skill):
        client = self._client

        self.delay = uo.rules.skill_delay(skill)

        for x in self.skills:
            self._client.send(p.SkillLock(x, SKILL_LOCK_DOWN))
        self._client.send(p.SkillLock(skill, SKILL_LOCK_UP))

        d = UseSkill(client, skill).deferred
        d.addCallbacks(self._skill_finished, self._failure)

    def _next_skill(self):
        client = self._client

        self.skill, self.skills = self.skills[0], self.skills[1:]
        self._do_skill(self.skill)

    def _check_skill(self):
        client = self._client
        player = client.world.player

        total = 0
        for x in self.skills:
            if x in player.skills:
                total += player.skills[x].base

        if total == 0:
            self.skills.append(self.skill)
            self._next_skill()
        else:
            self._do_skill(self.skill)

    def _skill_finished(self, result):
        reactor.callLater(self.delay, self._check_skill)
