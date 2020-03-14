# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *


class Character:
    """
    服务端角色对象基础数据接口类
    """
    def __init__(self):
        pass

    def Relive(self):
        """
        满血复活
        """
        self.HP = self.BaseHP

    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        pass

    def GetScriptName(self):
        return self.__class__.__name__