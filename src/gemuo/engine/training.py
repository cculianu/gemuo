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

from uo.skills import *
import uo.packets as p
import uo.rules
from uo.entity import *
from gemuo.engine import Engine
from gemuo.timer import TimerEvent

class UseSkill(Engine):
    def __init__(self, client, skill):
        Engine.__init__(self, client)
        self._skill = skill
        self._world = client.world
        self._target_mutex = client.target_mutex
        self._target_locked = False
        self._targets = self._find_skill_targets(skill)

        if self._targets is None:
            print "Error: no target found for", SKILL_NAMES[skill]
            self._failure()
            return

        if len(self._targets) == 0:
            # the skill doesn't need a target
            self._use_skill(skill)
        else:
            # wait for target cursor reservation before invoking the
            # skill
            self._target_mutex.get_target(self._target_ok, self._target_abort)

    def abort(self):
        if self._target_locked:
            self._target_mutex.put_target()
        self._failure()

    def _distance2(self, position):
        player = self._world.player.position
        dx = player.x - position.x
        dy = player.y - position.y
        return dx*dx + dy*dy

    def _find_dagger(self):
        return self._world.find_player_item(lambda x: x.is_dagger())

    def _find_instrument(self):
        x = self._world.find_player_item(lambda x: x.is_instrument())
        if x is not None: return x
        return self._world.find_reachable_item(lambda x: x.is_instrument())

    def _find_food(self):
        x = self._world.find_player_item(lambda x: x.is_food())
        if x is not None: return x
        return self._world.find_reachable_item(lambda x: x.is_food())

    def _find_crook(self):
        return self._world.find_player_item(lambda x: x.item_id == ITEM_CROOK)

    def _find_mobiles(self):
        mobiles = list(filter(lambda x: x != self._world.player and x.position is not None,
                              self._world.mobiles()))
        mobiles.sort(lambda a, b: cmp(self._distance2(a.position), self._distance2(b.position)))
        return mobiles

    def _find_animals(self):
        animals = filter(lambda x: x.is_animal() and self._distance2(x.position) <= 64,
                         self._find_mobiles())
        animals.sort(lambda a, b: cmp(self._distance2(a.position), self._distance2(b.position)))
        return animals

    def _find_neutral_animals(self):
        return filter(lambda x: x.notoriety == 3,
                      self._find_animals())

    def _find_skill_targets(self, skill):
        targets = []
        count = 1

        if skill in (SKILL_HIDING, SKILL_MUSICIANSHIP, SKILL_PEACEMAKING,
                     SKILL_SPIRIT_SPEAK):
            count = 0
        elif skill == SKILL_DETECT_HIDDEN:
            targets.append(self._world.player)
        elif skill in (SKILL_ANATOMY, SKILL_EVAL_INT):
            targets = self._find_mobiles()
        elif skill == SKILL_TASTE_ID:
            food = self._find_food()
            if food is not None:
                targets.append(food)
        elif skill == SKILL_PROVOCATION:
            targets.extend(self._find_neutral_animals())
            count = 2

            if len(targets) == 1 and self._world.player is not None:
                # target self if less than 2 animals found
                targets.append(self._world.player)
        elif skill == SKILL_ANIMAL_LORE:
            targets.extend(self._find_animals())
        elif skill == SKILL_HERDING:
            targets.extend(self._find_animals())
            count = 2

            if len(targets) > 0:
                targets = (targets[0], self._world.player)
        else:
            dagger = self._find_dagger()
            if dagger is not None:
                targets.append(dagger)

        if len(targets) < count: return None

        return targets[:count]

    def _use_skill(self, skill):
        assert self._target_locked == bool(self._targets)

        print "train skill", SKILL_NAMES[skill]

        if skill == SKILL_MUSICIANSHIP:
            instrument = self._find_instrument()
            if instrument is not None:
                self._client.send(p.Use(instrument.serial))
                self._success()
            else:
                print "No instrument!"
                self._client.send(p.Use(SERIAL_PLAYER | self._world.player.serial))
                self._failure()
                return

        elif skill == SKILL_HERDING:
            crook = self._find_crook()
            if crook is not None:
                self._client.send(p.Use(crook.serial))
            else:
                print "No crook!"
                self._client.send(p.Use(SERIAL_PLAYER | self._world.player.serial))
                self._target_mutex.put_target()
                self._failure()
                return

        else:
            self._client.send(p.UseSkill(skill))

            if len(self._targets) == 0:
                self._success()

    def _target_ok(self):
        """Called by the TargetMutex class when this engine receives
        the target cursor reservation."""
        if self.finished():
            self._target_mutex.put_target()
            return

        self._target_locked = True
        self._use_skill(self._skill)

    def _target_abort(self):
        """Called by the TargetMutex class when this engine times
        out."""
        if self.finished():
            return

        self._failure()

    def _on_target_request(self, allow_ground, target_id, flags):
        if not self._target_locked: return

        if False:
            # point to floor

            position = self._world.player.position
            if position is None:
                self._target_mutex.put_target()
                self._failure()
                return

            self._client.send(p.TargetResponse(1, target_id, flags, 0,
                                               position.x, position.y, position.z, 0))
            self._target_mutex.put_target()
            self._success()
        else:
            assert self._targets

            # get the next target from the list and send TargetResponse
            target, self._targets = self._targets[0], self._targets[1:]
            self._client.send(p.TargetResponse(0, target_id, flags, target.serial,
                                               0xffff, 0xffff, 0xffff, 0))

            if not self._targets:
                # all targets have been used: return the target cursor
                # reservation
                self._target_mutex.put_target()
                self._success()

    def on_packet(self, packet):
        if isinstance(packet, p.TargetRequest):
            self._on_target_request(packet.allow_ground, packet.target_id,
                                    packet.flags)

class UseStealth(Engine, TimerEvent):
    """Stealth is a special case: it can only be used if the player is
    hidden already.  So this sub-engine hides first (unless already
    hidden), and then attempts to use the Stealth skill unless the
    player is revealed."""

    def __init__(self, client):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)

        self._player = client.world.player
        self._waiting = False

        if self._player.is_hidden():
            self._client.send(p.UseSkill(SKILL_STEALTH))
        else:
            self._client.send(p.UseSkill(SKILL_HIDING))
        self._schedule(0.5)

    def abort(self):
        self._unschedule()
        self._failure()

    def tick(self):
        if not self._player.is_hidden():
            # we have been revealed or hiding has failed; finish this
            # engine for now
            self._success()
        elif self._waiting:
            # next stealth attempt
            self._waiting = False
            self._client.send(p.UseSkill(SKILL_STEALTH))
            self._schedule(0.5)
        else:
            # still hidden; wait for skill delay
            self._waiting = True
            self._schedule(10)

class SkillTraining(Engine, TimerEvent):
    """Train one or more skills."""

    def __init__(self, client, skills, round_robin=False):
        Engine.__init__(self, client)
        TimerEvent.__init__(self, client)
        self._world = client.world
        self._skills = list(skills)
        self._use = None
        self.round_robin = round_robin

        # get current skill values
        client.send(p.MobileQuery(0x05, self._world.player.serial))

        # refresh backpack contents, in case we need a target
        if self._world.backpack() is not None:
            client.send(p.Use(self._world.backpack().serial))

        if self._world.player.skills:
            self._check_skills(self._world.player.skills)

        self.tick()

    def abort(self):
        if self._use is not None:
            self._use.abort()
        self._unschedule()
        self._failure()

    def _check_skills(self, skills):
        total = 0
        down = 0
        for skill in skills.itervalues():
            total += skill.base
            if skill.lock == SKILL_LOCK_DOWN:
                down += skill.base

        line = "Skills:"
        for skill_id in self._skills:
            name = SKILL_NAMES[skill_id]

            if skill_id not in skills:
                print "No value for skill", skill_id
                self._failure()
                return

            skill = skills[skill_id]

            line += "  %s=%d" % (name, skill.base)
            if skill.base >= skill.cap:
                print "Done with skill", name
                self._skills.remove(skill_id)
            elif skill.lock != SKILL_LOCK_UP:
                print "Skill is locked:", name
                self._failure()
                return

        line += "  (total=%d, down=%d)" % (total, down)
        print line

        if len(self._skills) == 0:
            if self._use is not None:
                self._use.abort()
            self._unschedule()
            self._success()
            return

        if total >= 7000 and down == 0:
            print "No skills down"
            if self._use is not None:
                self._use.abort()
            self._unschedule()
            self._failure()

    def _next_skill(self):
        if len(self._skills) == 0: return None

        skill = self._skills[0]
        if self.round_robin:
            # rotate the skill list
            self._skills = self._skills[1:] + [skill]
        return skill

    def tick(self):
        assert self._use is None

        self._current = skill = self._next_skill()
        assert skill is not None

        # create a UseSkill sub-engine and wait for its completion
        if skill == SKILL_STEALTH:
            self._use = UseStealth(self._client)
        else:
            self._use = UseSkill(self._client, skill)

        if self._use.finished():
            # if finished within the constructor, then our
            # on_engine_{success,failure} method won't catch it;
            # special handling below:
            result = self._use.result()
            self._use = None
            if result:
                self._schedule(uo.rules.skill_delay(self._current))
            else:
                self._schedule(1)

    def on_skill_update(self, skills):
        self._check_skills(skills)

    def on_engine_success(self, engine, *args, **keywords):
        if self._use is not None and engine == self._use:
            # the UseSkill engine has finished: schedule the next
            # skill
            self._use = None
            self._schedule(uo.rules.skill_delay(self._current))

    def on_engine_failure(self, engine, *args, **keywords):
        if self._use is not None and engine == self._use:
            # the UseSkill engine has failed: retry soon
            self._use = None
            self._schedule(1)
