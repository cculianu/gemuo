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
    class StatSkillJojo < UO::TimerEvent
        def initialize(skill1, skill2)
            super()
            @skills = [ skill1, skill2 ]
        end

        def tick
            return unless @current

            # use skill
            $client << UO::Packet::TextCommand.new(0x24, @current.to_s)

            restart(1.5)
            $client.timer << self
        end

        def on_ingame
            # get skills
            $client << UO::Packet::MobileQuery.new(0x05, $client.player.serial)
        end

        def on_skill_update
            if @current
                value = $client.skill(@other)
                if value == nil || value.value == 0
                    @current = nil
                    @other = nil
                end
            end
            
            unless @current
                # decide which is current
                values = @skills.collect do
                    |skill_id|
                    value = $client.skill(skill_id)
                    unless value
                        puts "Error: no value for skill #{skill_id}\n"
                        return
                    end
                    value
                end

                if values[0].base < values[1].base
                    @current = @skills[0]
                    @other = @skills[1]
                else
                    @current = @skills[1]
                    @other = @skills[0]
                end

                $client << UO::Packet::ChangeSkillLock.new(@current, UO::LOCK_UP)
                $client << UO::Packet::ChangeSkillLock.new(@other, UO::LOCK_DOWN)

                tick
            end
        end

        def find_dagger
            $client.each_item do
                |item|
                #puts "item=0x%x\n" % item.item_id
                return item if item.item_id == 0xf52
            end
            nil
        end

        def on_target(allow_ground, target_id, flags)
            item = find_dagger
            unless item
                puts "Error: no dagger found\n"
                return
            end
            puts "Serial=0x%x\n" % item.serial
            $client << UO::Packet::TargetResponse.new(0, target_id, flags, item.serial,
                                                      0xffff, 0xffff, 0xffff, 0)
        end
    end
end
