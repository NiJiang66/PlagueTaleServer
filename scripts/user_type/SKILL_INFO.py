# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *


class TSkillInfo(dict):
    def __init__(self):
        dict.__init__(self)

    def asDict(self):
        Data = {
            "SkillId":          self["SkillId"],
            "SpawnPos":         self["SpawnPos"],
            "TargetPos":        self["TargetPos"],
        }
        return Data

    def createFromDict(self, DictData):
        self["SkillId"] = DictData["SkillId"]
        self["SpawnPos"] = DictData["SpawnPos"]
        self["TargetPos"] = DictData["TargetPos"]
        return self

class SKILL_INFO_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dct):
        return TSkillInfo().createFromDict(dct)

    def isSameType(self, obj):
        return isinstance(obj, TSkillInfo)

    def getDictFromObj(self, obj):
        return obj.asDict()




SkillInfoInst = SKILL_INFO_PICKLER()