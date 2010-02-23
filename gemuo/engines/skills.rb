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
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

require 'gemuo/rules'
require 'gemuo/timer'
require 'gemuo/engines/base'

module GemUO::Engines
    class EasySkills < Base
        include GemUO::TimerEvent

        def initialize(client, skills)
            super(client)
            @skills = skills
            @targets = 0
        end

        def on_ingame
            # get skills
            @client << GemUO::Packet::MobileQuery.new(0x05, @client.world.player.serial)

            tick
        end

        def check_skills
            sum = 0
            down = 0
            @client.world.skills.each_value do
                |skill|
                sum += skill.base
                down += skill.base if skill.lock == GemUO::SKILL_LOCK_DOWN
            end

            line = "Skills:"
            @skills.sort.each do
                |id|
                skill = @client.world.skill(id)
                unless skill
                    puts "No value for skill #{id}\n"
                    stop
                    @client.signal_fire(:on_engine_failed, self)
                    return
                end

                line << "  #{skill.name}=#{skill.base}"
                if skill.base == skill.cap
                    puts "Done with skill #{skill.name}\n"
                    @skills.delete(id)
                elsif skill.lock != GemUO::SKILL_LOCK_UP
                    puts "Skill #{skill.name} is locked\n"
                    stop
                    @client.signal_fire(:on_engine_failed, self)
                    return
                end
            end
            line << "  (sum=#{sum}, down=#{down})\n"
            puts line

            if @skills.empty?
                stop
                @client.signal_fire(:on_engine_complete, self)
                return
            end

            if sum >= 7000 && down == 0
                puts "No skills down\n"
                stop
                @client.signal_fire(:on_engine_failed, self)
                return
            end
        end

        def find_dagger
            backpack = @client.world.backpack
            return unless backpack
            @client.world.each_item_in(backpack) do
                |item|
                return item if item.dagger?
            end
            nil
        end

        def distance2(position)
            player = @client.world.player.position
            dx = player.x - position.x
            dy = player.y - position.y
            return dx*dx + dy*dy
        end

        def find_instrument
            backpack = @client.world.backpack
            return unless backpack
            @client.world.each_item_in(backpack) do
                |item|
                return item if item.instrument?
            end
            nil
        end

        def find_mobiles
            mobiles = []
            @client.world.each_mobile do
                |mobile|
                mobiles << mobile unless mobile == @client.world.player || mobile.position == nil
            end
            mobiles.sort! do
                |a,b|
                distance2(a.position) <=> distance2(b.position)
            end
            return mobiles
        end

        def find_animals
            mobiles = []
            @client.world.each_mobile do
                |mobile|
                mobiles << mobile if mobile.notoriety == 3 && mobile.animal? && distance2(mobile.position) <= 49
            end
            mobiles.sort! do
                |a,b|
                distance2(a.position) <=> distance2(b.position)
            end
            return mobiles
        end

        def find_skill_targets(skill)
            targets = []
            count = 1

            case skill
            when GemUO::SKILL_HIDING, GemUO::SKILL_DETECT_HIDDEN, GemUO::SKILL_MUSICIANSHIP
                count = 0

            when GemUO::SKILL_ANATOMY, GemUO::SKILL_EVAL_INT, GemUO::SKILL_PEACEMAKING
                targets = find_mobiles

            when GemUO::SKILL_PROVOCATION
                targets = find_animals
                count = 2

                if targets.length == 1 && @client.world.player
                    # target self if less than 2 animals found
                    targets << @client.world.player
                end

            else
                dagger = find_dagger
                targets << dagger if dagger
            end

            return nil if targets.length < count
            return targets.slice(0, count)
        end

        def tick
            # roll skills
            @current = @skills.shift
            @skills << @current

            # use skill
            puts "skill #{GemUO::SKILL_NAMES[@current]}\n"

            @targets = find_skill_targets(@current)
            unless @targets
                puts "Error: no target found for #{@current}\n"
                restart(1)
                @client.timer << self
                return
            end

            case @current
            when GemUO::SKILL_MUSICIANSHIP
                instrument = find_instrument
                if instrument
                    @client << GemUO::Packet::Use.new(instrument.serial)
                else
                    puts "No instrument!\n"
                end

            else
                @client << GemUO::Packet::TextCommand.new(0x24, @current.to_s)
            end

            restart(GemUO::Rules.skill_delay(@current))
            @client.timer << self
        end

        def on_skill_update
            check_skills

            # get backpack
            if @client.world.backpack
                @client << GemUO::Packet::Use.new(@client.world.backpack.serial)
            else
                puts "no backpack\n"
                # open paperdoll
                @client << GemUO::Packet::Use.new(GemUO::SERIAL_PLAYER | @client.world.player.serial)
            end
        end

        def on_target(allow_ground, target_id, flags)
            return unless @targets

            skill = @current
            @current = nil

            target = nil
            case skill
            when GemUO::SKILL_DETECT_HIDDEN
                # point to floor
                p = @client.world.player.position
                @client << GemUO::Packet::TargetResponse.new(1, target_id, flags, 0,
                                                          p.x, p.y, p.z, 0)
                return

            else
                target = @targets.shift
                return unless target
            end

            @client << GemUO::Packet::TargetResponse.new(0, target_id, flags, target.serial,
                                                         0xffff, 0xffff, 0xffff, 0)
        end
    end
end
