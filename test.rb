$:.unshift(File.dirname($0) + '/glue')
$:.unshift(File.dirname($0))

require 'uo/client'
require 'uo/engines'

raise "syntax: test.rb host port username password" unless ARGV.length == 4

$client = UO::Client.new(ARGV[0], ARGV[1], nil,
                         ARGV[2], ARGV[3])

class TestTimer < UO::TimerEvent
    def tick
        puts "tick!\n"
    end
end

class Ingame
    def on_ingame
        UO::Engines::SimpleWalk.new($client, UO::Position.new(1420, 1675))
        $client.timer << TestTimer.new(10)
    end
end

$client.signal_connect(Ingame.new)

$client.run
