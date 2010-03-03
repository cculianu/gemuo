#!/usr/bin/python

from uo.skills import *
from gemuo.simple import SimpleClient
from gemuo.engine.stats import StatLock
from gemuo.engine.training import SkillTraining
from gemuo.engine.messages import PrintMessages
from gemuo.engine.guards import Guards

skills = (
    SKILL_PROVOCATION,
    SKILL_PROVOCATION,
    SKILL_PEACEMAKING,
)

client = SimpleClient()
PrintMessages(client)
Guards(client)
StatLock(client, (100, 25, 100))
st = SkillTraining(client, skills, round_robin=True)
client.until(st.finished)
