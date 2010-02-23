#!/usr/bin/python

from uo.skills import *
from gemuo.simple import SimpleClient
from gemuo.engine.training import SkillTraining
from gemuo.engine.messages import PrintMessages

skills = (
    SKILL_HIDING,
    SKILL_DETECT_HIDDEN,
    SKILL_ANATOMY,
    SKILL_EVAL_INT,
    SKILL_ITEM_ID,
    SKILL_ARMS_LORE,
)

client = SimpleClient()
PrintMessages(client)
st = SkillTraining(client, skills, round_robin=False)
client.until(st.finished)
