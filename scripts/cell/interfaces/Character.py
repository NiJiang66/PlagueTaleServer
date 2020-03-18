# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import math
import Math
import time
import random
from SKILL_INFO import TSkillInfo
from CalculateLib import *
from D_Good import *


class Character:
    """
    服务端角色对象基础数据接口类
    """
    def __init__(self):
        # 保存力量Buff定时器Id
        self.PowerBuffTid = -1
        self.SpeedBuffTid = -1

    def GetScriptName(self):
        return self.__class__.__name__

    def Relive(self):
        """
        满血复活
        """
        self.HP = self.BaseHP

    def Attack(self, SkillInfo):
        """
        进行攻击
        """
        SpawnPos = U2KVec(SkillInfo["SpawnPos"])
        TargetPos = U2KVec(SkillInfo["TargetPos"])

        #将技能与普通攻击分开
        #如果是普通攻击，不生成技能
        #if SkillInfo["SkillId"] == 0:
            # 告诉所有客户端播放动画
         #   self.allClients.OnAttack(0)
         #   return

        # 生成的技能攻击力要乘上力量加成
        Props = {
            "SkillId" : SkillInfo["SkillId"],
            "OwnerId" : self.id,
            "Damage" : int(60 * self.PowerRatio),
            "SpawnPos": SpawnPos,
            "TargetPos": TargetPos
        }
        # 生成技能
        KBEngine.createEntity("PtSkill", self.spaceID, SpawnPos, Math.Vector3(0, 0, 0), Props)
        # 告诉所有客户端播放动画
        self.allClients.OnAttack(SkillInfo["SkillId"])


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
            # 如果怪物血值为0 , 死后原地生成随机物品
            if self.GetScriptName() == "PtMonster":
                # 生成物品类型
                GoodType = random.randint(0, 2)
                # 生成细分种类Id
                KindId = random.randint(0, GetKindNumByType(GoodType))
                # 根据上面两个数据获取物品Id
                GoodId = GetGoodIdByTypeKind(GoodType, KindId)
                # 生成掉落物
                Props = {
                    "GoodId" : GoodId,
                    "GoodType": GoodType
                }
                KBEngine.createEntity("PtFlob", self.spaceID, self.position, Math.Vector3(0, 0, 0), Props)
                INFO_MSG("Create PtFlob When PtMonster AcceptDamage to HP == 0. " )
                self.destroy()
        else:
            self.HP -= FactDamage

    def PutOnEquip(self, KindId):
        """
        穿上装备
        :param KindId:细分类型id
        """
        # 根据设备的KindId获取效果数据
        Feature = GetFeatureByTypeKind(EGoodType.Equip.value, KindId)
        # 根据装备不同添加效果
        if KindId is EEquipKind.Helmet.value:
            # 头盔增加生命上限
            self.BaseHP += Feature
        elif KindId is EEquipKind.Armor.value:
            # 铠甲增加防御值
            self.Defense += Feature
        elif KindId is EEquipKind.Shoes.value:
            # 增加速度加成
            self.SpeedRatio += Feature

    def TakeOffEquip(self, KindId):
        """
        脱下装备
        :param KindId:细分类型id
        """
        # 根据装备的KindId获取效果数据
        Feature = GetFeatureByTypeKind(EGoodType.Equip.value, KindId)
        # 根据装备不同添加效果
        if KindId is EEquipKind.Helmet.value:
            # 头盔减少生命上限
            self.BaseHP -= Feature
            # 如果当前血值大于最大血值, 修改当前血值为最大血值
            if self.HP > self.BaseHP:
                self.HP = self.BaseHP
        elif KindId is EEquipKind.Armor.value:
            # 铠甲减少防御值
            self.Defense -= Feature
        elif KindId is EEquipKind.Shoes.value:
            # 减少速度加成
            self.SpeedRatio -= Feature

    def AddBuff(self, KindId):
        """
        添加技能
        :param KindId:细分类型id
        """
        # 根据Buff的KindId获取效果数据
        Feature = GetFeatureByTypeKind(EGoodType.Buff.value, KindId)
        # 根据Buff不同添加效果
        if KindId is EBuffKind.Cure.value:
            # 增加100血值
            NowHP = self.HP
            NowHP += 100
            if NowHP > self.BaseHP:
                NowHP = self.BaseHP
            self.HP = NowHP
        elif KindId is EBuffKind.Power.value:
            # 增加力量加成, 持续20秒, 使用定时器
            # 如果力量定时Id存在, 说明已经有加成了, 先删除定时器, 再重新启动定时器
            if self.PowerBuffTid is not -1:
                self.delTimer(self.PowerBuffTid)
                self.PowerBuffTid = self.addTimer(20, 0, KindId)
            else:
                # 先增加效果
                self.PowerRatio += Feature
                # 再添加定时器
                self.PowerBuffTid = self.addTimer(20, 0, KindId)
        elif KindId is EBuffKind.Speed.value:
            # 逻辑类似上面
            if self.SpeedBuffTid is not -1:
                self.delTimer(self.SpeedBuffTid)
                self.SpeedBuffTid = self.addTimer(20, 0, KindId)
            else:
                self.SpeedRatio += Feature
                self.SpeedBuffTid = self.addTimer(20, 0, KindId)

    def onTimer(self, tid, userArg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        # 如果是力量加成
        if tid is self.PowerBuffTid:
            # 减少力量加成, 可以考虑直接写成恢复为1.0, 减少判断
            Feature = GetFeatureByTypeKind(EGoodType.Buff.value, userArg)
            self.PowerRatio -= Feature
            # 重置力量定时器为 -1
            self.PowerBuffTid = -1
        elif tid is self.SpeedBuffTid:
            Feature = GetFeatureByTypeKind(EGoodType.Buff.value, userArg)
            # 重置速度加成
            self.SpeedRatio -= Feature
            # 重置速度定时Id
            self.SpeedBuffTid = -1
