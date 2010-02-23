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

require 'gemuo/timer'
require 'gemuo/engines/base'

module GemUO::Engines
    class Delayed < Base
        include GemUO::TimerEvent

        def initialize(client, delay, &block)
            super(client)
            @delay = delay
            @block = block
        end

        def on_ingame
            restart(@delay)
            @client.timer << self
        end

        def tick
            stop
            @block.call
        end
    end
end
