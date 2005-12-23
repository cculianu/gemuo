#
#  libuoclient-ruby
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

module UO::Engines
    class EasySkills < UO::TimerEvent
        def initialize(client, skills)
            @client = client
            @skills = skills
        end

        def start
            @client.signal_connect(self)

            # get skills
            @client << UO::Packet::MobileQuery.new(0x05, @client.world.player.serial)

            tick
        end
        def stop
            @client.signal_disconnect(self)
        end

        def check_skills
            if @skills.empty?
                stop
                @client.signal_fire(:on_engine_complete, self)
                return
            end

            $stdout << "Skills:"
            @skills.sort.each do
                |id|
                skill = @client.world.skill(id)
                $stdout << "  #{UO::SKILL_NAMES(id)}=#{skill ? skill.base : '?'}"
                @skills.delete(id) if skill && skill.base == skill.cap
            end
            $stdout << "\n"
        end

        def skill_delay(skill)
            case skill
            when UO::SKILL_HIDING
                return 9

            else
                return 1.2
            end
        end

        def tick
            # roll skills
            @current = @skills.shift
            @skills << @current

            # use skill
            puts "skill #{UO::SKILL_NAMES[@current]}\n"
            @client << UO::Packet::TextCommand.new(0x24, @current.to_s)

            restart(skill_delay(@current))
            @client.timer << self
        end

        def on_skill_update
            check_skills

            # get backpack
            if @client.world.backpack
                @client << UO::Packet::Use.new(@client.world.backpack.serial)
            end
        end

        def find_dagger
            backpack = @client.world.backpack
            return unless backpack
            @client.world.each_item_in(backpack) do
                |item|
                return item if item.item_id == 0xf52
            end
            nil
        end

        def distance2(position)
            dx = @player.position.x - position.x
            dy = @player.position.y - position.y
            return dx*dx + dy*dy
        end

        def find_mobile
            mobiles = []
            @player = @client.world.player
            @client.world.each_mobile do
                |mobile|
                mobiles << mobile unless mobile == @player || mobile.position == nil
            end
            return if mobiles.empty?
            mobiles.sort! do
                |a,b|
                distance2(a.position) <=> distance2(b.position)
            end
            mobiles[0]
        end

        def on_target(allow_ground, target_id, flags)
            target = nil
            if @current == UO::SKILL_DETECT_HIDDEN
                # point to floor
                p = @client.world.player.position
                @client << UO::Packet::TargetResponse.new(1, target_id, flags, 0,
                                                          p.x, p.y, p.z, 0)
                return
            elsif @current == UO::SKILL_ANATOMY ||
                    @current == UO::SKILL_EVAL_INT
                target = find_mobile
            else
                target = find_dagger
            end

            unless target
                puts "Error: no target found for #{@current}\n"
                return
            end

            @client << UO::Packet::TargetResponse.new(0, target_id, flags, target.serial,
                                                      0xffff, 0xffff, 0xffff, 0)
        end
    end
end
