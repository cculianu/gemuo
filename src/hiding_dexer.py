#!/usr/bin/python

from uo.skills import *
from gemuo.simple import SimpleClient
from gemuo.engine.stats import StatLock
from gemuo.engine.training import SkillTraining
from gemuo.engine.messages import PrintMessages

skills = (
    SKILL_HIDING,
    SKILL_ANATOMY,
    SKILL_ARMS_LORE,
    SKILL_DETECT_HIDDEN,
    SKILL_ITEM_ID,
    SKILL_EVAL_INT,
)

client = SimpleClient()
PrintMessages(client)
StatLock(client, (100, 100, 25))
st = SkillTraining(client, skills, round_robin=False)
client.until(st.finished)
