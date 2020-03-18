# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.Character import Character
from interfaces.Motion import Motion
from interfaces.AI import AI

class PtMonster(KBEngine.Entity,
             Character,
             Motion,
             AI
             ):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        Character.__init__(self)
        Motion.__init__(self)
        AI.__init__(self)

        # 临时代码
        #self.addTimer(0, 1, 0)

    def onTimer(self, tid, userArg):
        """
        定时器回调函数
        :param tid:
        :param userArg:
        """
        # 分发到有onTimer的父类
        AI.onTimer(self, tid, userArg)
        Character.onTimer(self, tid, userArg)
        #Motion.onTimer(self, tid, userArg)