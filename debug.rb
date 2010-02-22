$:.unshift(File.dirname($0))

require 'gemuo/simple'
require 'gemuo/engines/debug'

client = GemUO::SimpleClient.new

GemUO::Engines::EntityDump.new(client).start
GemUO::Engines::WalkDump.new(client).start
GemUO::Engines::MessageDump.new(client).start

client.run
