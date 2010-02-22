$:.unshift(File.dirname($0))

require 'gemuo/client'
require 'gemuo/engines/debug'

raise "syntax: test.rb host port username password charname" unless ARGV.length == 5

client = GemUO::Client.new(ARGV[0], ARGV[1], nil,
                           ARGV[2], ARGV[3], ARGV[4])

GemUO::Engines::EntityDump.new(client).start
GemUO::Engines::WalkDump.new(client).start
GemUO::Engines::MessageDump.new(client).start

client.run
