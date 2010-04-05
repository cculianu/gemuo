#!/usr/bin/python

from twisted.internet import reactor
from uo.skills import *
from uo.spells import *
from uo.entity import *
import uo.packets as p
import uo.rules
from gemuo.simple import simple_run
from gemuo.entity import Item
from gemuo.engine import Engine
from gemuo.defer import deferred_skill
from gemuo.target import Target, SendTarget
from gemuo.engine.messages import PrintMessages
from gemuo.engine.guards import Guards
from gemuo.engine.watch import Watch
from gemuo.engine.stats import StatLock
from gemuo.engine.player import QuerySkills

class CastSpell(Engine):
    def __init__(self, client, spell):
        Engine.__init__(self, client)

        client.send(p.Cast(spell))
        reactor.callLater(2, self._success)

class CastTargetSpell(Engine):
    def __init__(self, client, spell, target):
        Engine.__init__(self, client)

        self.spell = spell
        self.target = target

        self.target_mutex = client.target_mutex
        self.target_mutex.get_target(self._target_ok, self._target_abort)

    def _target_ok(self):
        self._client.send(p.Cast(self.spell))

        self.engine = SendTarget(self._client, Target(serial=self.target.serial))
        self.engine.deferred.addCallbacks(self._target_sent, self._target_failed)

    def _target_abort(self):
        self.engine.abort()
        self._failure()

    def _target_sent(self, result):
        self.target_mutex.put_target()
        reactor.callLater(2, self._success)

    def _target_failed(self, fail):
        self.target_mutex.put_target()
        self._failure(fail)

class NeedMana(Engine):
    def __init__(self, client, mana):
        Engine.__init__(self, client)

        self.player = client.world.player
        self.mana = mana

        d = deferred_skill(client, SKILL_MEDITATION)
        d.addCallbacks(self._got_meditation_skill, self._failure)

    def _got_meditation_skill(self, meditation):
        skill = meditation.value

        # calculate the optimal skill gain percentage
        min_percent, max_percent = 900 - skill, 1200 - skill
        if min_percent < 0:
            min_percent = 0
        if max_percent < 0:
            max_percent = 0
        elif max_percent > 1000:
            max_percent = 1000

        if self.player.stats is not None:
            intelligence = self.player.stats[2]
        else:
            intelligence = 50

        min_mana = (min_percent * intelligence) / 1000
        max_mana = (max_percent * intelligence) / 1000

        if self.mana < max_mana:
            self.mana = max_mana

        self._check()

    def _check(self):
        if self.player.mana is None:
            self._failure()
        elif self.player.mana.value >= self.mana:
            self._success()
        elif self.player.stats is None or self.player.stats[2] < self.mana:
            print "Not enough INT"
            self._failure()
        else:
            self._client.send(p.UseSkill(SKILL_MEDITATION))
            delay = uo.rules.skill_delay(SKILL_MEDITATION)
            reactor.callLater(10, self._check)

def select_circle(skill):
    if skill < 300:
        return None
    if skill < 350:
        return 3
    if skill < 500:
        return 4
    if skill < 600:
        return 5
    if skill < 750:
        return 6
    if skill < 960:
        return 7
    return 8

SPELLS = (
    None,
    None,
    None,
    (11, SPELL_LIGHTNING, True),
    (14, SPELL_INCOGNITO, False),
    (20, SPELL_INVISIBILITY, True),
    (40, SPELL_FLAME_STRIKE, True),
    #(50, SPELL_X, True),
)

def select_spell(skill):
    circle = select_circle(skill)
    if circle is None: return None
    return SPELLS[circle - 1]

def find_target(world):
    for e in world.iter_entities_at(world.player.position.x + 1, world.player.position.y - 3):
        if isinstance(e, Item) and e.item_id in (0x1f03, 0x1f04):
            return e
    return None

class AutoMagery(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

        self._next()

    def _next(self):
        d = deferred_skill(self._client, SKILL_MAGERY)
        d.addCallbacks(self._got_magery_skill, self._failure)

    def _got_magery_skill(self, magery):
        skill = magery.value
        spell = select_spell(skill)
        if spell is None:
            print "No spell"
            self._failure()
            return

        mana, self.spell, self.target = spell
        d = NeedMana(self._client, mana).deferred
        d.addCallbacks(self._meditated, self._failure)

    def _meditated(self, result):
        client = self._client

        if self.target:
            target = find_target(client.world)
            if target is None:
                print "No target"
                self._failure()
                return

            d = CastTargetSpell(client, self.spell, target).deferred
        else:
            d = CastSpell(client, self.spell).deferred
        d.addCallbacks(self._casted, self._failure)

    def _casted(self, result):
        self._next()

def run(client):
    PrintMessages(client)
    Guards(client)
    Watch(client)
    StatLock(client, (100, 25, 100))
    return AutoMagery(client)

simple_run(run)
