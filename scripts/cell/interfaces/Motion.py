# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from ANIM_INFO import TAnimInfo
import math
import Math
import time
import random

class Motion:
    """
    服务端角色对象移动逻辑接口类
    """
    def __init__(self):
        #初始化下一次移动的时间
        self.NextMoveTime = int(time.time() + random.randint(10, 15))



    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        pass

    def AnimUpdate(self, AnimInfo):
        """
        客户端调用更新动画参数
        :param AnimInfo: 动画参数
        """
        self.otherClients.OnAnimUpdate(AnimInfo)

    def StopMotion(self):
        """
        停止移动
        """
        if self.IsMoving:
            self.cancelController("Movement")
            self.IsMoving = False


    def GoToPosition(self, DestPos, MoveSpeed = 2.5, LimitDist = 0.0):
        """
        移动到目标点
        :param DestPos: 目标点
        :param LimitDist: 停止移动距离
        """
        # 如果正在移动, 停止移动
        if self.IsMoving:
            self.StopMotion()

        self.MoveSpeed = MoveSpeed

        self.moveToPoint(DestPos, self.MoveSpeed, LimitDist, None, True, False)

        # 广播动画数据(速度和方向)到客户端
        AnimInfo = TAnimInfo().createFromDict({"Speed" : self.MoveSpeed*100, "Direction" : 0.0})
        self.allClients.OnAnimUpdate(AnimInfo)


    def GoToEntity(self, TargetId, MoveSpeed = 2.5, LimitDist = 0.0):
        """
        移动到entity位置
        :param TargetId: 目标id
        :param LimitDist: 限制距离
        """
        # 如果正在移动, 停止移动
        if self.IsMoving:
            self.StopMotion()

        # 根据Id获取对象
        TargetEntity = KBEngine.entities.get(TargetId)
        if TargetEntity is None:
            DEBUG_MSG("%s::GoToEntity: not found targetID=%i" % (self.Name, TargetId))
            return

        #判断和实体的距离是否小于停止距离
        if TargetEntity.position.distTo(self.position) <= LimitDist:
            return

        self.IsMoving = True
        # 追逐敌人的攻击速度
        self.MoveSpeed = MoveSpeed #5.0

        self.moveToEntity(TargetId, self.MoveSpeed, LimitDist, None, True, False)

        # 广播移动速度
        AnimInfo = TAnimInfo().createFromDict({"Speed": self.MoveSpeed*100, "Direction": 0.0})
        # 广播动作信息
        self.allClients.OnAnimUpdate(AnimInfo)

    def RandomWander(self):
        """
        随机移动
        """
        # 如果正在移动
        if self.IsMoving:
            return False

        # 如果没有到下一次移动的时间
        if time.time() < self.NextMoveTime:
            return False

        # 更新下一次移动时间
        self.NextMoveTime = int(time.time() + random.randint(10, 15))

        while True:
            """
            # 在1500米半径内寻找目标点, 如果有导航, 使用导航寻找
            if self.canNavigate():
                DestPosGroup = self.getRandomPoints(self.position, 15, 1, 0)
                if len(DestPosGroup) == 0:
                    self.nextMoveTime = int(time.time() + random.randint(5, 15))
                    return False
                DestPos = DestPosGroup[0]
            else:
            """
            # 获取随机移动方向
            rnd = random.random()
            a = 10.0 + 10.0 * rnd  # 移动半径距离在1000 - 2000米内
            b = 360.0 * rnd  # 随机一个角度
            x = a * math.cos(b)  # 半径 * 正余玄
            z = a * math.sin(b)

            DestPos = Math.Vector3(self.position.x + x, self.position.y, self.position.z + z)

            # 判断是否越界
            if DestPos.x > 50 or DestPos.x < -50 or DestPos.z > 50 or DestPos.z < -50:
                continue

            # 移动到点
            self.GoToPosition(DestPos, 2.5)

            # 跳出
            break



    # --------------------------------------------------------------------------------------------
    #                             move的Callbacks
    # --------------------------------------------------------------------------------------------
    def onMove(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
        """
        # DEBUG_MSG("%s::onMove: %i controllerId =%i, userarg=%s" % \
        #				(self.GetScriptName(), self.id, controllerId, userarg))
        self.IsMoving = True

    def onMoveFailure(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity一次移动完成时均会调用此接口
        """
        DEBUG_MSG("%s::onMoveFailure: %i controllerId =%i, userarg=%s" % (
            self.GetScriptName(), self.id, controllerId, userarg))

        self.IsMoving = False

        # 广播移动速度
        AnimInfo = TAnimInfo().createFromDict({"Speed": 0.0, "Direction": 0.0})
        self.allClients.OnAnimUpdate(AnimInfo)

    def onMoveOver(self, controllerId, userarg):
        """
        KBEngine method.
        使用引擎的任何移动相关接口， 在entity移动结束时均会调用此接口
        """
        self.IsMoving = False

        # 广播移动速度
        AnimInfo = TAnimInfo().createFromDict({"Speed": 0.0, "Direction": 0.0})
        self.allClients.OnAnimUpdate(AnimInfo)