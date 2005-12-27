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

module UO
    class TimerEvent
        def initialize(seconds = nil)
            restart(seconds) if seconds
        end

        def restart(seconds)
            @due = Time.new.to_f + seconds
        end

        def due
            @due
        end

        def tick
            raise 'implement this'
        end

        def <=>(other)
            raise TypeError.new unless other.kind_of?(TimerEvent)
            return @due <=> other.due
        end
    end

    class TimerEvent2
        def initialize(seconds, target, method, *args)
            @due = Time.new.to_f + seconds
            @target = target
            @method = method
            @args = args
        end

        def due
            @due
        end

        def tick
            @target.send(@method, @args)
        ensure
            @target, @method, @args = nil, nil, nil
        end
    end

    class Timer
        def initialize
            @events = []
        end

        def <<(event)
            @events << event
            @events.sort!
        end

        def tick
            now = Time.new.to_f
            until @events.empty? || now < @events.last.due
                @events.pop.tick
            end
        end
    end
end
