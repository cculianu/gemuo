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
    class Main
        def initialize(client, engine)
            @client = client
            @engine = engine
            @ingame = false
            @started = false
        end

        def start
            return if @started
            @started = true

            @client.signal_connect(self)
            @engine.start if @ingame
        end
        def stop
            return unless @started

            @engine.stop if @ingame
            @client.signal_disconnect(self)
        end

        def on_ingame
            @ingame = true
            @engine.start
        end

        def on_engine_complete(engine)
            return unless engine == @engine
            puts "engine complete, exiting\n"
            exit 0
        end

        def on_engine_failed(engine)
            return unless engine == @engine
            puts "engine failed, exiting\n"
            exit 1
        end
    end
end
