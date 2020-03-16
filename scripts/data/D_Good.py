# -*- coding: utf-8 -*-
from enum import Enum

#物品数据配置表（需维护）
GoodDatas = {
    0 : {"Name" : "寒冰之石", "Type" : 0, "Kind" : 0, "Number" : 1, "Feature" : 20},
    1 : {"Name" : "雷霆之光", "Type" : 0, "Kind" : 1, "Number" : 1, "Feature" : 20},
    2 : {"Name" : "无尽之刃", "Type" : 0, "Kind" : 2, "Number" : 1, "Feature" : 30},
    3 : {"Name" : "恢复之术", "Type" : 0, "Kind" : 3, "Number" : 1, "Feature" : 30},
    4 : {"Name" : "治愈", "Type" : 1, "Kind" : 0, "Number" : 3, "Feature" : 100},
    5 : {"Name" : "力量", "Type" : 1, "Kind" : 1, "Number" : 3, "Feature" : 0.5},
    6 : {"Name" : "速度", "Type" : 1, "Kind" : 2, "Number" : 3, "Feature" : 0.5},
    7 : {"Name" : "长剑", "Type" : 2, "Kind" : 0, "Number" : 0, "Feature" : 100},
    8 : {"Name" : "盾牌", "Type" : 2, "Kind" : 1, "Number" : 0, "Feature" : 5},
    9 : {"Name" : "能量球", "Type" : 2, "Kind" : 2, "Number" : 0, "Feature" : 0.5},
}

class EBagType(Enum):
    """
    背包种类
    """
    MainBag  = 0
    SkillBag = 1
    BuffBag  = 2
    EquipBag = 3


class EGoodType(Enum):
    """
    物品种类
    """
    Skill = 0
    Buff = 1
    Equip = 2

class EEquipKind(Enum):
    """
    装备种类
    """
    Helmet = 0
    Armor = 1
    Shoes = 2
    Weapon = 3

class EBuffKind(Enum):
    """
    Buff种类
    """
    Cure = 0
    Power = 1
    Speed = 2

class EReduceResult(Enum):
    """
    减少(使用)物品结果, 能在客户端减少的物品只有Buff
    """
    # 使用物品成功
    Succeed = 0
    # 不存在对应物品
    NoGood = 1

def GetKindNumByType(GoodType):
    """
    根据传入的物品类型输出该类物品有多少细分种类
    :param GoodType:物品类型
    :return:细分种类数量
    """
    KindNum = 0
    for id, item in GoodDatas.items():
        if item["Type"] is GoodType:
            KindNum += 1
    return KindNum

def GetGoodIdByTypeKind(GoodType, KindId):
    """
    根据传入的物品类型和细分种类Id获取物品Id
    :param GoodType:
    :param KindId:
    :return:
    """
    for id, item in GoodDatas.items():
        if item["Type"] is GoodType and item["Kind"] is KindId:
            return id
    return 0

def GetKindIdByGoodId(GoodId):
    """
    根据GoodId获取KindId
    :param GoodId:
    :return:
    """
    if GoodId in GoodDatas:
        return GoodDatas[GoodId]["Kind"]
    return -1

def GetTypeByGoodId(GoodId):
    """
    根据GoodId获取GoodType
    :param GoodId:
    :return:
    """
    if GoodId in GoodDatas:
        return GoodDatas[GoodId]["Type"]
    return -1


def GetFeatureByTypeKind(GoodType, KindId):
    """
    根据GoodType和KindId获取效果数据
    :param GoodType:
    :param KindId:
    :return:
    """
    for id, item in GoodDatas.items():
        if item["Type"] is GoodType and item["Kind"] is KindId:
            return item["Feature"]
    return 0
