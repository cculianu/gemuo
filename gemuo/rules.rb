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

require 'gemuo/skills'

module GemUO::Rules
    T2A = true

    module_function

    def skill_delay(skill)
        case skill
        when GemUO::SKILL_HIDING, GemUO::SKILL_PEACEMAKING
            return 11

        when GemUO::SKILL_PROVOCATION
            return 13

        else
            return T2A ? 11 : 1.5
        end
    end
end
