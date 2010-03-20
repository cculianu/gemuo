#!/usr/bin/python

from uo.skills import *
from uo.spells import *
from uo.entity import *
import uo.packets as p
import uo.rules
from gemuo.simple import SimpleClient
from gemuo.entity import Item
from gemuo.engine import Engine
from gemuo.engine.messages import PrintMessages
from gemuo.engine.guards import Guards
from gemuo.engine.watch import Watch
from gemuo.engine.util import FinishCallback, DelayedCallback
from gemuo.engine.player import QuerySkills

class CastSpell(Engine):
    def __init__(self, client, spell):
        Engine.__init__(self, client)

        client.send(p.Cast(spell))
        DelayedCallback(client, 2, self._casted)

    def _casted(self):
        self._success()

class CastTargetSpell(Engine):
    def __init__(self, client, spell, target):
        Engine.__init__(self, client)

        self.spell = spell
        self.target = target

        self.target_locked = False
        self.target_mutex = client.target_mutex
        self.target_mutex.get_target(self._target_ok, self._target_abort)

    def _target_ok(self):
        self.target_locked = True
        self._client.send(p.Cast(self.spell))

    def _target_abort(self):
        self._failure()

    def _on_target_request(self, allow_ground, target_id, flags):
        if not self.target_locked: return

        client = self._client
        client.send(p.TargetResponse(0, target_id, flags, self.target.serial,
                                     0xffff, 0xffff, 0xffff, 0))
        self.target_mutex.put_target()

        DelayedCallback(client, 2, self._success)

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._on_target_request(packet.allow_ground, packet.target_id,
                                    packet.flags)

class NeedMana(Engine):
    def __init__(self, client, mana):
        Engine.__init__(self, client)

        self.mana = mana
        self.player = client.world.player
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
            DelayedCallback(client, 10, self._check)

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

        if client.world.player.skills is None:
            FinishCallback(client, QuerySkills(client), self._got_skills)
        else:
            self._next()

    def _got_skills(self, success):
        if not success:
            self._failure()
            return

        self._next()

    def _next(self):
        client = self._client
        player = client.world.player
        if player.skills is None or SKILL_MAGERY not in player.skills:
            print "No magery skill"
            self._failure()
            return

        skill = player.skills[SKILL_MAGERY].value
        spell = select_spell(skill)
        if spell is None:
            print "No spell"
            self._failure()
            return

        mana, self.spell, self.target = spell
        FinishCallback(client, NeedMana(client, mana), self._meditated)

    def _meditated(self, success):
        if not success:
            self._failure()
            return

        client = self._client

        if self.target:
            target = find_target(client.world)
            if target is None:
                print "No target"
                self._failure()
                return

            FinishCallback(client, CastTargetSpell(client, self.spell, target), self._casted)
        else:
            FinishCallback(client, CastSpell(client, self.spell), self._casted)

    def _casted(self, success):
        if not success:
            self._failure()
            return

        self._next()

client = SimpleClient()

PrintMessages(client)
Guards(client)
Watch(client)
client.until(AutoMagery(client).finished)
