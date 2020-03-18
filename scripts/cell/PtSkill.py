import KBEngine
from KBEDebug import *
import math
import Math
import time
import random

class PtSkill(KBEngine.Entity):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        self.MoveSpeed = 25
        self.Enable()
        #目前不需要技能拥有者id
        self.OwnerId = 0


    def Enable(self):
        """
        激活技能运动
        """
        # 在定时器内触发检测, 不开启循环
        self.addTimer(0, 0, 1)

        if self.SkillId == 0:
            pass

        #判断是不是需要移动技能
        if self.TargetPos != self.SpawnPos:
            # 获取移动方向
            #MoveDirection = self.TargetPos - self.SpawnPos
            #MoveDirection.normalise()
            # 修改目标位置为方向的6000单位处
            #self.TargetPos = self.SpawnPos + MoveDirection * 60.0
            self.moveToPoint(self.TargetPos, self.MoveSpeed, 0.0, None, True, True)


    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------

    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        if userArg == 1:
            if self.TerritoryControllerId <= 0:
                self.AddTerritory()

    def onMoveOver(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity移动结束时均会调用此接口
        """
        # 删除碰撞
        self.DelTerritory()
        # 技能移动结束, 销毁技能 客户端销毁技能, 不对任何角色造成伤害
        self.destroy()

    def onMove(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
        """
        pass

    def onMoveFailure(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
        """
        pass

    def AddTerritory(self):
        """
        添加领地
        进入领地范围的某些entity将视为敌人
        """
        # 在这里判断是哪种技能
        self.TerritoryControllerId = self.addProximity(2, 0, 0)

        if self.TerritoryControllerId <= 0:
            ERROR_MSG("Skill %i::addTerritory: %i, range=%i, is error!" % (self.SkillId, self.id, 2))
        else:
            INFO_MSG(
                "Skill %i::addTerritory: %i range=%i, id=%i." % (self.SkillId, self.id, 2, self.TerritoryControllerId))

    def DelTerritory(self):
        """
        删除领地
        """
        if self.TerritoryControllerId > 0:
            self.cancelController(self.TerritoryControllerId)
            self.TerritoryControllerId = 0

    def onEnterTrap(self, entityEntering, range_xz, range_y, controllerID, userarg):
        """
        有entity进入trap
        :param entityEntering:
        :param range_xz:
        :param range_y:
        :param controllerID:
        :param userarg:
        """
        if controllerID != self.TerritoryControllerId:
            return

        # 忽略自己
        if entityEntering.id == self.OwnerId:
            #如果是加血技能,加血技能id为4
            #if self.SkillId == 3:
             #   TargetH = PentityEntering.HP + self.Damage
             #   if TargetH > PentityEntering.BaseHP:
             #       entityEntering.HP = PentityEntering.BaseHP
             #   else:
             #       entityEntering.HP = TargetH

                # 删除碰撞
              #  self.DelTerritory()
                # 销毁技能 客户端销毁技能
              #  self.destroy()
            return

        # 筛选一下，必须是角色
        if entityEntering.GetScriptName() != "PtRole" and entityEntering.GetScriptName() != "PtMonster":
            return

        # 筛选是否血值已经为 0
        if entityEntering.HP == 0:
            return

        # 判断y轴是否匹配
        if abs(entityEntering.position.y - self.position.y) > 2:
            return

        # 告诉角色减血
        entityEntering.AcceptDamage(self.Damage, self.OwnerId)
        # 删除碰撞
        self.DelTerritory()
        # 销毁技能 客户端销毁技能
        self.destroy()

    def onLeaveTrap(self, entityLeaving, range_xz, range_y, controllerID, userarg):
        """
        有entity离开trap
        :param entityLeaving:
        :param range_xz:
        :param range_y:
        :param controllerID:
        :param userarg:
        """
        if controllerID != self.TerritoryControllerId:
            return


    def GetScriptName(self):
        return self.__class__.__name__

