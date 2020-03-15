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

    def Attack(self, SkillInfo):
        """
        进行攻击
        """
        # 告诉所有客户端播放动画
        self.allClients.OnAttack()


    def AcceptDamage(self, Damage, SenderId):
        """
        接受伤害, 获取发送伤害者的ID
        :param Damage: 伤害值
        :param SenderId: 发送者ID
        """
        FactDamage = Damage - self.Defense
        if FactDamage < 0:
            return

        # 减血, 如果血值小于等于实际伤害
        if self.HP <= FactDamage:
            self.HP = 0
            # 如果怪物血值为0 , 直接死
            if self.GetScriptName() == "PtMonster":
                self.destroy()
        else:
            self.HP -= FactDamage



    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        pass

    def GetScriptName(self):
        return self.__class__.__name__