# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import math
import Math
import time
import random
from enum import Enum
from CalculateLib import *

class EAIState(Enum):
    """
    AI状态枚举, 死亡状态不考虑
    """
    Wander = 0
    Chase = 1
    Attack = 2

class AI:
    """
    服务端NPC的AI逻辑接口类
    """
    def __init__(self):
        # 视野内的同类, 用于计算更智能的群体移动
        self.FriendList = []
        # 设定攻击范围
        self.AttackRange = 3
        # 添加攻击时间间隔, 每隔三秒攻击一次
        self.AttackSpace = 0
        # 设定丢失范围
        self.MissingRange = 20
        # 设定怪物视野触发范围
        self.TerritoryArea = 10
        # 激活怪物AI状态管理器
        self.Enable()

    def Enable(self):
        """
        激活AI, 该AI管理随机移动, 进行战斗, 死亡失活等效果
        """
        # 添加攻击时间间隔, 每隔三秒攻击一次
        self.AttackSpace = 0
        # 激活触发器(视野)
        self.addTimer(0, 0, 0)
        # 激活心跳
        self.UpdateStateID = self.addTimer(random.randint(0, 1), 1, 1)

    def Disable(self):
        """
        失活, 禁止更新, 失活触发器
        """
        #删除视野触发器
        self.DelTerritory()
        #删除心跳计时器
        self.delTimer(self.UpdateStateID)
        self.UpdateStateID = 0
        #初始化状态
        self.AIState = EAIState.Wander.value
        self.TargetId = -1
        self.AttackSpace = 0


    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        # 添加触发器(视野)，这里只会被激活一次
        if userArg is 0:
            if self.TerritoryControllerId <= 0:
                self.AddTerritory()
        # 循环心跳
        if userArg is 1:
            self.UpdateState()

    def UpdateState(self):
        """
        心跳函数, 怪物状态 0 自由移动 1 追逐玩家 2 攻击玩家
        """
        if self.AIState is EAIState.Wander.value:
            self.StateWander()
        elif self.AIState is EAIState.Chase.value:
            self.StateChase()
        elif self.AIState is EAIState.Attack.value:
            self.StateAttack()

    def StateWander(self):
        """
        自由移动
        """
        # 如果视野没有打开, 添加视野
        if self.TerritoryControllerId <= 0:
            self.addTimer(0, 0, 0)
        # 寻找一次目标
        TempTargetId, TargetDistance = self.FindClosestTarget()
        # 如果目标为空
        if TempTargetId is -1:
            # 随机移动
            self.RandomWander()
            return

        if TargetDistance <= self.AttackRange:
            self.TargetId = TempTargetId
            self.AIState = EAIState.Attack.value
        elif TargetDistance > self.AttackRange and TargetDistance < self.MissingRange:
            self.TargetId = TempTargetId
            self.AIState = EAIState.Chase.value
        else:
            self.AIState = EAIState.Wander
            # 随机移动
            self.RandomWander()

    def StateChase(self):
        """
        追逐玩家
        """
        # 追逐的时候目标Id一定存在
        # 获取目标实体
        TargetEntity = KBEngine.entities.get(self.TargetId)

        # 是否需要更改目标
        IsNeedChangeTarget = False
        # 如果目标已经为空
        if TargetEntity is None:
            # 把目标Id从列表移除
            self.TargetList.remove(self.TargetId)
            # 设置需要更改目标
            IsNeedChangeTarget = True

        # 如果目标存在但是血值为0
        if TargetEntity is not None and TargetEntity.HP is 0:
            IsNeedChangeTarget = True

        # 如果需要更改目标
        if IsNeedChangeTarget:
            # 运行寻找目标函数
            self.TargetId, TargetDistance = self.FindClosestTarget()
            # 如果寻找到的目标为无
            if self.TargetId is -1:
                # 进入巡逻状态
                self.AIState = EAIState.Wander.value
            else:
                # 根据距离判定追逐还是攻击
                if TargetDistance < self.AttackRange:
                    self.AIState = EAIState.Attack.value
                else:
                    self.AIState = EAIState.Chase.value
        else:
            # 不需要更改目标, 检查距离
            TargetDistance = self.position.distTo(TargetEntity.position)
            # 根据距离判定追逐还是攻击
            if TargetDistance < self.AttackRange:
                self.AIState = EAIState.Attack.value
            elif TargetDistance > self.MissingRange:
                self.AIState = EAIState.Wander.value
                self.TargetId = -1
            else:
                self.AIState = EAIState.Chase.value

        # 计算最终移动位置
        if self.AIState is EAIState.Chase.value:
            FriendPos = self.GetChasePos(TargetEntity.position)
            self.GoToPosition(FriendPos, 3.75)

    def StateAttack(self):
        """
        攻击玩家
        """
        # 获取目标实体
        TargetEntity = KBEngine.entities.get(self.TargetId)

        # 是否需要更改目标
        IsNeedChangeTarget = False
        # 如果目标已经为空
        if TargetEntity is None:
            # 把目标Id从列表移除
            self.TargetList.remove(self.TargetId)
            # 设置需要更改目标
            IsNeedChangeTarget = True

        # 如果目标存在但是血值为0
        if TargetEntity is not None and TargetEntity.HP is 0:
            IsNeedChangeTarget = True

        # 如果需要更改目标
        if IsNeedChangeTarget:
            # 运行寻找目标函数
            self.TargetId, TargetDistance = self.FindClosestTarget()
            # 如果寻找到的目标为无
            if self.TargetId is -1:
                # 进入巡逻状态
                self.AIState = EAIState.Wander.value
            else:
                # 根据距离判定追逐还是攻击
                if TargetDistance < self.AttackRange:
                    self.AIState = EAIState.Attack.value
                else:
                    self.AIState = EAIState.Chase.value
        else:
            # 不需要更改目标, 检查距离
            TargetDistance = self.position.distTo(TargetEntity.position)
            # 根据距离判定追逐还是攻击
            if TargetDistance < self.AttackRange:
                self.AIState = EAIState.Attack.value
            elif TargetDistance > self.MissingRange:
                self.AIState = EAIState.Wander.value
                self.TargetId = -1
            else:
                self.AIState = EAIState.Chase.value

        # 如果状态依然是攻击
        if self.AIState is EAIState.Attack.value:
            # 直接将角度设定到目标角度, 由客户端来插值
            DirectionVector = K2UVec(TargetEntity.position - self.position)
            # 不计算高度
            DirectionVector2D = Math.Vector2(DirectionVector.x, DirectionVector.y)
            # 获取Yaw值, 这个是 0 - 360 度
            DirectionYaw = CalcVector2DAngle(Math.Vector2(1, 0), DirectionVector2D)
            # 更新Yaw值到旋转
            self.direction.z = math.radians(DirectionYaw)
            # 如果计时器不到
            if self.AttackSpace is not 0:
                self.AttackSpace -= 1
            else:
                # 广播客户端播放攻击动画
                self.allClients.OnAttack()
                # 给目标减血
                TargetEntity.AcceptDamage(self.Damage, self.id)
                # 重新计数
                self.AttackSpace = 3
        else:
            # 如果不是攻击状态, 修改攻击计时器为0
            self.AttackSpace = 0





    def AddTerritory(self):
        """
        添加领地，（视野）触发器
        进入领地范围的某些entity将视为敌人
        """
        self.TerritoryControllerId = self.addProximity(self.TerritoryArea, 0, 0)

    def DelTerritory(self):
        """
        删除领地，（视野）触发器
        """
        if self.TerritoryControllerId > 0:
            self.cancelController(self.TerritoryControllerId)
            self.TerritoryControllerId = 0
            INFO_MSG("%s::delTerritory: %i" % (self.GetScriptName(), self.id))

    def FindClosestTarget(self):
        """
        从目标列表寻找最近的目标Id
        :return: 目标Id和距离
        """
        # 定义临时距离
        MinDistance = 100
        # 定义获取到的角色Id
        FoundId = -1
        # 定义空链表保存已经被销毁的玩家id
        DisableList = []
        for EntityId in self.TargetList:
            TempEntity = KBEngine.entities.get(EntityId)
            # 如果获取为空, 说明玩家角色已经被销毁, 需要从目标列表移除
            if TempEntity is None:
                DisableList.append(EntityId)
                continue
            # 如果血值为空, 不从目标列表移除, 因为有可能会复活
            if TempEntity.HP is 0:
                continue
            else:
                # 血值不为空则判定距离是否最小
                # 获取该角色与自己的距离
                TempDistance = self.position.distTo(TempEntity.position)
                # 如果距离小于最小距离
                if TempDistance < MinDistance:
                    # 更新最小距离
                    MinDistance = TempDistance
                    # 更新寻找的Id
                    FoundId = EntityId
        # 从目标列表移除被销毁了的玩家角色
        for EntityId in DisableList:
            self.TargetList.remove(EntityId)
        # 返回目标Id和距离
        return FoundId, MinDistance

    def GetChasePos(self, TargetPos):
        """
        获取追逐最终位置
        :return:
        """
        # 获取周边怪物列表对象的位置
        DisableList = []
        # 保存怪物角度
        FriendAngles = []
        # 保存角度平均值
        AverageAngle = 0
        for EntityId in self.FriendList:
            FriendMonster = KBEngine.entities.get(EntityId)
            if FriendMonster is None:
                DisableList.append(EntityId)
                continue
            # 这里要判定和自己同一目标的角色
            if FriendMonster.TargetId is self.TargetId and (FriendMonster.AIState is EAIState.Chase.value or FriendMonster.AIState is EAIState.Attack.value):
                # 计算各个怪物到目标的方向夹角
                FriendDirection = K2UVec(FriendMonster.position - TargetPos)
                FriendDirection2D = Math.Vector2(FriendDirection.x, FriendDirection.y)
                DirectionAngle = CalcVector2DAngle(Math.Vector2(1, 0), FriendDirection2D)
                AverageAngle += DirectionAngle
                FriendAngles.append(DirectionAngle)
        for EntityId in DisableList:
            self.FriendList.remove(EntityId)

        # 计算自己到方向向量的夹角
        SelfDirection = K2UVec(self.position - TargetPos)
        SelfDirection2D = Math.Vector2(SelfDirection.x, SelfDirection.y)
        SelfAngle = CalcVector2DAngle(Math.Vector2(1, 0), SelfDirection2D)

        # 如果有其他敌人
        if len(FriendAngles) > 0:
            # 排序
            FriendAngles.sort()
            # 计算平均角度, 作为中位角度
            AverageAngle += SelfAngle
            AverageAngle /= (len(FriendAngles) + 1)
            SpaceAngle = 360 / (len(FriendAngles) + 1)
            # 获取当前角度到中位角度是第几个
            AngleIndex = 0
            AverageIndex = 0
            for index, value in enumerate(FriendAngles):
                if AverageAngle < value:
                    AverageIndex = index
                if SelfAngle < value:
                    AngleIndex = index
            # 通过和中位之间的距离计算最终到达角度
            if SelfAngle < AverageAngle:
                FinalAngle = math.radians(AverageAngle - (AverageIndex - AngleIndex) * SpaceAngle)
                # 计算方向向量, 返回位置
                FinalDirection = Math.Vector3(math.cos(FinalAngle), 0, math.sin(FinalAngle))
                return TargetPos + FinalDirection * (self.AttackRange - 0.5)
            else:
                FinalAngle = math.radians(AverageAngle + (AngleIndex - AverageIndex) * SpaceAngle)
                # 计算方向向量, 返回位置
                FinalDirection = Math.Vector3(math.cos(FinalAngle), 0, math.sin(FinalAngle))
                return TargetPos + FinalDirection * (self.AttackRange - 0.5)
        else:
            # 如果没有其他敌人，直接返回方向前两米的位置
            SelfDirection = U2KVec(SelfDirection)
            SelfDirection.normalise()
            return TargetPos + SelfDirection * (self.AttackRange - 0.5)


    # --------------------------------------------------------------------------------------------
    #                             (视野)触发器的Callbacks
    # --------------------------------------------------------------------------------------------

    def onEnterTrap(self, entityEntering, range_xz, range_y, controllerID, userarg):
        """
        有entity进入trap
        :param entityEntering:
        :param range_xz:
        :param range_y:
        :param controllerID:
        :param userarg:
        """
        # 判断是否为自己的触发器id，不是的话直接返回
        if controllerID != self.TerritoryControllerId:
            return

        # 如果是存活的怪物, 添加到朋友列表
        if not entityEntering.isDestroyed and entityEntering.GetScriptName() is "PtMonster" and entityEntering.id not in self.FriendList:
            self.FriendList.append(entityEntering.id)

        # 筛选一下，必须是Avatar，并且没有dead
        if entityEntering.isDestroyed or entityEntering.GetScriptName() != "PtRole":
            return

        # 到这一定是PtRole玩家，则添加实体id到目标列表
        if entityEntering.id not in self.TargetList:
            self.TargetList.append(entityEntering.id)

        # 如果当前目标id为-1, 以及进入视野领域的目标血值不为0, 设定该玩家实体为锁定的目标, 改状态为追逐
        if self.TargetId is -1 and entityEntering.HP is not 0:
            self.TargetId = entityEntering.id
            self.AIState = EAIState.Chase.value

    def onLeaveTrap(self, entityLeaving, range_xz, range_y, controllerID, userarg):
        """
        有entity离开trap
        :param entityLeaving:
        :param range_xz:
        :param range_y:
        :param controllerID:
        :param userarg:
        """
        # 判断是否为自己的触发器id，不是的话直接返回
        if controllerID != self.TerritoryControllerId:
            return

        # 如果是存活的怪物, 从朋友列表移除
        if not entityEntering.isDestroyed and entityEntering.GetScriptName() is "PtMonster" and entityEntering.id in self.FriendList:
            self.FriendList.remove(entityEntering.id)

        # 筛选一下，必须是Avatar，并且没有dead
        if entityEntering.isDestroyed or entityEntering.GetScriptName() != "PtRole":
            return

        # 到这一定是PtRole玩家，则将实体id从目标列表移除
        if entityEntering.id not in self.TargetList:
            self.TargetList.remove(entityEntering.id)


    def onWitnessed(self, isWitnessed):
        """
        KBEngine method.
        此实体是否被观察者(player)观察到, 此接口主要是提供给服务器做一些性能方面的优化工作，
        在通常情况下，一些entity不被任何客户端所观察到的时候， 他们不需要做任何工作， 利用此接口
        可以在适当的时候激活或者停止这个entity的任意行为。
        @param isWitnessed	: 为false时， entity脱离了任何观察者的观察
        """
        #被玩家观察到时，激活AI，反之失活AI
        if isWitnessed:
            self.Enable()
        else:
            self.Disable()