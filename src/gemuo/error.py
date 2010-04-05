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

class Timeout(Exception):
    def __init__(self, message='Timeout'):
        Exception.__init__(self, message)

class NoSuchEntity(Exception):
    """An entity was not found."""
    def __init__(self, message='No such entity'):
        Exception.__init__(self, message)

class NoSkills(Exception):
    """The server didn't send skill values upon request."""
    def __init__(self, message='No skill values'):
        Exception.__init__(self, message)

class SkillLocked(Exception):
    def __init__(self, message='Skill is locked'):
        Exception.__init__(self, message)
