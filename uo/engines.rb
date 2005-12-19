module UO::Engines
    class SimpleWalk
        def initialize(client, destination)
            @destination = destination
            @client = client
            @client.signal_connect(self)
            next_walk
        end

        def distance2(position)
            dx = @destination.x - position.x
            dy = @destination.y - position.y
            return dx*dx + dy*dy
        end

        def direction_from(position)
            if @destination.x < position.x
                if @destination.y < position.y
                    return UO::NORTH_WEST
                elsif @destination.y > position.y
                    return UO::SOUTH_WEST
                else
                    return UO::WEST
                end
            elsif @destination.x > position.x
                if @destination.y < position.y
                    return UO::NORTH_EAST
                elsif @destination.y > position.y
                    return UO::SOUTH_EAST
                else
                    return UO::EAST
                end
            else
                if @destination.y < position.y
                    return UO::NORTH
                elsif @destination.y > position.y
                    return UO::SOUTH
                else
                    return nil
                end
            end
        end

        def next_walk
            m = @client.player
            return unless m
            position = m.position
            return unless position
            puts "now at #{position.x}, #{position.y}\n"
            direction = direction_from(position)
            if direction == nil
                @client.signal_disconnect(self)
                return
            end
            direction |= UO::RUNNING if distance2(position) >= 4
            @client.walk(direction)
        end

        def on_walk_reject(client, *args)
            @client.signal_disconnect(self)
        end

        def on_walk_ack(client, *args)
            next_walk
        end
    end
end
