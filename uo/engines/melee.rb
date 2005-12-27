#
#  GemUO
#  $Id$
#
#  (c) 2005 Max Kellermann <max@duempel.org>
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
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

require 'uo/engines/blocking'

module GemUO::Engines
    class Melee < GemUO::Engines::Blocking
        PRIMARY = [ GemUO::SKILL_SWORDS, GemUO::SKILL_MACING,
                    GemUO::SKILL_FENCING, GemUO::SKILL_WRESTLING ]
        SECONDARY = [ GemUO::SKILL_TACTICS, GemUO::SKILL_ANATOMY,
                      GemUO::SKILL_LUMBERJACKING, GemUO::SKILL_HEALING,
                      GemUO::SKILL_PARRY ]

        def initialize(client, target_serial, passive)
            super(client)
            @target_serial = target_serial
            @passive = passive
        end

        def arm_for_skill(skill_id)
            # XXX
        end

        def run
            loop do
                # check skill values
                primary = []
                done = []
                secondary = []

                skills.each_value do
                    |skill|
                    next if skill.lock != GemUO::SKILL_LOCK_UP
                    if PRIMARY.include?(skill.id)
                        if skill.base < skill.cap && skill.lock == GemUO::SKILL_LOCK_UP
                            primary << skill.id
                        else
                            done << skill.id
                        end
                    elsif SECONDARY.include?(skill.id)
                        if skill.base < skill.cap && skill.lock == GemUO::SKILL_LOCK_UP
                            secondary << skill.id 
                        end
                    end
                end

                unless @passive
                    if primary.empty? && secondary.empty?
                        return true
                    end

                    if skill_free == 0
                        raise "No skillpoints free"
                    end

                    if primary.empty? && done.empty?
                        raise "No primary skills available"
                    end
                end

                # determine next training skill
                primary.sort!
                done.sort!

                unless @passive
                    line = "Melee skills:"
                    [primary, secondary].flatten.each do
                        |skill_id|
                        skill = skills[skill_id]
                        line << "  #{skill.name}=#{skill.base}"
                    end
                    line << "\n"
                    puts line
                end

                current = primary.empty? ? done.last : primary.last

                arm_for_skill(current)

                # check target health
                target = @client.world.entity(@target_serial)
                raise "Target not found" unless target

                target_hits = target.hits
                puts "target_hits=#{target_hits}\n"
                raise "No health info for target" unless target_hits

                if target_hits.value <= (target_hits.max * 2) / 3
                    # disable war mode
                    @client << GemUO::Packet::WarMode.new(false)

                    # heal target
                    if secondary.include?(GemUO::SKILL_HEALING) ||
                            (skills[GemUO::SKILL_HEALING] &&
                             skills[GemUO::SKILL_HEALING].value >= 300)
                        # got healing skill
                        puts "Healing target #{target}\n"

                        bandage = item_in_backpack(0xe21)
                        puts "bandage=#{bandage}\n"
                        if bandage
                            use_and_target(bandage, target)
                        else
                            puts "No bandage in backpack\n"
                        end
                    else
                        # no healing skill available, wait for target to heal itself
                    end

                    sleep(13)
                    puts "after heal sleep\n"

                    next
                end

                # check my health
                player = @client.world.player
                raise "Player not found" unless player

                player_hits = player.hits
                puts "player_hits=#{player_hits}\n"
                raise "No health info for player" unless target_hits

                if player_hits.value <= (player_hits.max * 2) / 3
                    # disable war mode
                    @client << GemUO::Packet::WarMode.new(false)

                    # heal myself
                    if secondary.include?(GemUO::SKILL_HEALING) ||
                            (skills[GemUO::SKILL_HEALING] &&
                             skills[GemUO::SKILL_HEALING].value >= 300)
                        # got healing skill
                        puts "Healing myself\n"
                    else
                        # no healing skill available, wait for target to heal us
                        sleep(13)
                    end

                    next
                end

                # attack
                @client << GemUO::Packet::WarMode.new(true)
                @client << GemUO::Packet::Attack.new(@target_serial)
                
                # idle for a moment
                sleep(2)
            end
        end
    end
end
