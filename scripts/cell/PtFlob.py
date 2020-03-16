import KBEngine
from KBEDebug import *
import math
import Math
import time
import random

class PtFlob(KBEngine.Entity):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        self.MoveSpeed = 5
        # 在定时器内触发检测, 不开启循环
        self.addTimer(0, 0, 1)

    def GetScriptName(self):
        return self.__class__.__name__

    def onTimer(self, tid, userArg):
        """
        引擎回调timer触发
        """
        if userArg == 1:
            if self.TerritoryControllerId <= 0:
                self.AddTerritory()


    def AddTerritory(self):
        """
        添加领地
        进入领地范围的某些entity将视为敌人
        """
        self.TerritoryControllerId = self.addProximity(6, 0, 0)
        if self.TerritoryControllerId <= 0:
            ERROR_MSG("Flob %i::addTerritory error!" % self.id)

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
        :return:
        """
        if controllerID != self.TerritoryControllerId:
            return

        # 筛选一下，必须是角色
        if entityEntering.GetScriptName() != "PtRole":
            return

        # 设定TargetId
        self.TargetId = entityEntering.id

        # 移动物体到对象
        self.moveToEntity(self.TargetId, self.MoveSpeed, 0.0, None, True, False)

    def onLeaveTrap(self, entityLeaving, range_xz, range_y, controllerID, userarg):
        """
        有entity离开trap
        :param entityLeaving:
        :param range_xz:
        :param range_y:
        :param controllerID:
        :param userarg:
        :return:
        """
        if controllerID != self.TerritoryControllerId:
            return

    def onMoveOver(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity移动结束时均会调用此接口
        """
        # 判断对象是否还存在
        if self.TargetId is -1:
            return

        TargetEntity = KBEngine.entities.get(self.TargetId)
        if TargetEntity is None:
            self.TargetId = -1
            return

        # 删除碰撞
        self.DelTerritory()
        # 物品移动结束, 告诉背包填充物品
        TargetEntity.base.IncreaseGood(self.GoodId, self.GoodType)
        # 销毁自己
        self.destroy()

    def onMove(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
        """
        # DEBUG_MSG("%s::onMove: %i controllerId =%i, userarg=%s" % \
        #				(self.getScriptName(), self.id, controllerId, userarg))
        pass

    def onMoveFailure(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
        """
        pass


