$:.unshift(File.dirname($0))

require 'gemuo/client'
require 'gemuo/engines/main'
require 'gemuo/engines/debug'

raise "syntax: test.rb host port username password charname" unless ARGV.length == 5

client = GemUO::Client.new(ARGV[0], ARGV[1], nil,
                           ARGV[2], ARGV[3], ARGV[4])

engines = []
engines << GemUO::Engines::EntityDump.new(client)
engines << GemUO::Engines::WalkDump.new(client)
engines << GemUO::Engines::MessageDump.new(client)

GemUO::Engines::Main.new(client, engines).start

client.run
