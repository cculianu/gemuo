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

require 'gemuo/engines/base'

module GemUO::Engines
    class Main < Base
        def initialize(client, engines)
            super(client)
            @engines = engines.kind_of?(Array) ? engines : [engines]
            @ingame = false
            @started = false
            @status = 0
        end

        def start
            return if @started
            @started = true

            super

            @engines.each do
                |engine|
                engine.start if @ingame
            end
        end
        def stop
            return unless @started

            @engines.reverse_each do
                |engine|
                engine.stop if @ingame
            end

            super
        end

        def on_ingame
            @ingame = true
            @engines.each do
                |engine|
                engine.start
            end
        end

        def on_engine_complete(engine)
            if @engines.include?(engine)
                @engines.delete(engine)
                puts "engine #{engine} complete\n"
                exit @status if @engines.empty?
            end
        end

        def on_engine_failed(engine)
            if @engines.include?(engine)
                @engines.delete(engine)
                @status = 1
                puts "engine #{engine} failed\n"
                exit @status if @engines.empty?
            end
        end
    end
end
