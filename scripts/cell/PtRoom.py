# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import math
import Math
import time
import random


class PtRoom(KBEngine.Space):
    """
    PtSpace的base部分，
    注意：它是一个实体，并不是真正的space，真正的space存在于cellapp的内存中，通过这个实体与之关联并操控space。
    """
    def __init__(self):
        KBEngine.Space.__init__(self)

        KBEngine.addSpaceGeometryMapping(self.spaceID, None, "spaces/MmoMapOne")
        # KBEngine.addSpaceGeometryMapping(self.spaceID, None, "spaces/MmoMapTwo")

        #随机创建多个Monster
        for i in range(random.randint(5, 8)):
            MonsterProps = {
                "Name": "怪物_" + str(i),
                "HP": 500,
            }
            KBEngine.createEntity("PtMonster", self.spaceID, Math.Vector3(random.randint(-7, 7), 0.7, random.randint(-7, 7)), Math.Vector3(0, 0, random.randint(0, 360)), MonsterProps)

    def GetScriptName(self):
        return self.__class__.__name__





