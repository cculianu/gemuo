#
#  Gemuo
#
#  (c) 2010 Kai Sassmannshausen <kai@sassie.org>
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

require 'gemuo/client'
require 'gemuo/spells'

raise "usage: whatsup.rb host port username password charname" unless ARGV.length == 5

$client = GemUO::Client.new(ARGV[0], ARGV[1], nil,
                            ARGV[2], ARGV[3], ARGV[4])

class Ingame
    def on_ingame
        $client.cast(GemUO::SPELL_CREATE_FOOD)
        exit
    end
end

$client.signal_connect(Ingame.new)

$client.run
