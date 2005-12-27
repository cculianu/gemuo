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

$:.unshift(File.dirname($0) + '/glue')
$:.unshift(File.dirname($0))

require 'uo/client'

raise "usage: whatsup.rb host port username password charname" unless ARGV.length == 5

$client = GemUO::Client.new(ARGV[0], ARGV[1], nil,
                            ARGV[2], ARGV[3], ARGV[4])

class WhatsUp < GemUO::TimerEvent
    def on_skill_update
        skills = $client.world.skills.values.sort.reverse
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
        exit
    end

    def start
        $client.signal_connect(self)
        $client << GemUO::Packet::MobileQuery.new(0x05, $client.world.player.serial)
    end
end

class Ingame
    def on_ingame
        e = WhatsUp.new
        e.start
    end
end

$client.signal_connect(Ingame.new)

$client.run
