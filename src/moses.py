#!/usr/bin/python

from uo.skills import *
from gemuo.simple import SimpleClient
from gemuo.engine.training import SkillTraining
from gemuo.engine.stats import StatLock
from gemuo.engine.messages import PrintMessages

skills = (
    SKILL_PROVOCATION,
    SKILL_PROVOCATION,
    SKILL_PEACEMAKING,
)

client = SimpleClient()
PrintMessages(client)
StatLock(client, (100, 25, 100))

st = SkillTraining(client, skills, round_robin=True)
SkillTraining(client, (SKILL_HERDING,))
client.until(st.finished)
