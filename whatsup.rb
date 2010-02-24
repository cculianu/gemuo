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

$:.unshift(File.dirname($0))

require 'gemuo/simple'
require 'gemuo/engines/base'

class WhatsUp < GemUO::Engines::Base
    def on_skill_update
        skills = @client.world.skills.values.sort.reverse
        puts "Skills:\n"
        sum = 0
        skills.each do
            |skill|
            next if skill.base == 0
            name = GemUO::SKILL_NAMES[skill.id]
            puts "#{name.rjust(20)}: #{skill.base.to_s.rjust(4)} (#{skill.lock})\n" 
            sum += skill.base
        end
        puts ' ' * 22 + sum.to_s + "\n"
        puts "\n"
        player = @client.world.player
        if player.alive?
            puts player.name + " is alive."
        else
            puts player.name + " is dead."
        end
        puts "\n"
        stop
    end

    def on_ingame
        @client << GemUO::Packet::MobileQuery.new(0x05, @client.world.player.serial)
    end
end

client = GemUO::SimpleClient.new
WhatsUp.new(client).start
client.run
