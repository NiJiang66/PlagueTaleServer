# -*- coding: utf-8 -*-
import math
import Math


def CrossVector(ArcVec, DesVec):
    """
    三维向量叉乘
    :param ArcVec:
    :param DesVec:
    :return:
    """
    return Math.Vector3(ArcVec.y * DesVec.z - ArcVec.z * DesVec.y, ArcVec.z * DesVec.x - ArcVec.x * DesVec.z, ArcVec.x * DesVec.y - ArcVec.y * DesVec.x)


def CrossVector2D(ArcVec, DesVec):
    """
    二维向量叉乘
    :param ArcVec:
    :param DesVec:
    :return: 只返回Z轴值
    """
    return ArcVec.x * DesVec.y - ArcVec.y * DesVec.x

def DotVector(ArcVec, DesVec):
    """
    三维向量点乘
    :param ArcVec:
    :param DesVec:
    :return:
    """
    return ArcVec.x * DesVec.x + ArcVec.y * DesVec.y + ArcVec.z * DesVec.z

def DotVector2D(ArcVec, DesVec):
    """
    二维向量点乘
    :param ArcVec:
    :param DesVec:
    :return:
    """
    return ArcVec.x * DesVec.x + ArcVec.y * DesVec.y


# math.degrees() 弧度转角度
# math.radians() 角度转弧度

def CalcVectorAngle(ArcVec, DesVec):
    """
    计算两个三维向量的顺时针夹角, 转换成0-360度返回
    :param ArcVec: 起始向量
    :param DesVec: 目标向量
    :return: 返回角度
    """
    ArcVec.normalise()
    DesVec.normalise()
    CrossValue = CrossVector(ArcVec, DesVec)
    Position = 1.0
    if CrossValue.Z < 0:
        Position = -1.0
    ResAngle = Position * math.degrees(math.acos(DotVector(ArcVec, DesVec)))
    if ResAngle < 0:
        ResAngle += 360.0
    return ResAngle


def CalcVector2DAngle(ArcVec, DesVec):
    """
    计算两个二维向量的顺时针夹角, 转换成0-360度返回
    :param ArcVec:
    :param DesVec:
    :return:
    """
    ArcVec.normalise()
    DesVec.normalise()
    CrossValue = CrossVector2D(ArcVec, DesVec)
    Position = 1.0
    if CrossValue < 0:
        Position = -1.0
    ResAngle = Position * math.degrees(math.acos(DotVector2D(ArcVec, DesVec)))
    if ResAngle < 0:
        ResAngle += 360.0
    return ResAngle


def K2UVec(ArcVec):
    """
    kbe的Vector转ue4的Vector
    :param ArcVec:
    :return:
    """
    return Math.Vector3(ArcVec.z * 100, ArcVec.x * 100, ArcVec.y * 100)

def U2KVec(ArcVec):
    """
    ue4的Vector转kbe的Vector
    :param ArcVec:
    :return:
    """
    return Math.Vector3(ArcVec.y * 0.01, ArcVec.z * 0.01, ArcVec.x * 0.01)

def K2URot(ArcRot):
    """
    kbe的旋转转ue4的旋转
    :param ArcRot:
    :return:
    """
    return Math.Vector3(math.degrees(ArcRot.y), math.degrees(ArcRot.z), math.degrees(ArcRot.x))

def U2KRot(ArcRot):
    """
    ue4的旋转转ue4的旋转
    :param ArcRot:
    :return:
    """
    return Math.Vector3(math.radians(ArcRot.z), math.radians(ArcRot.x), math.radians(ArcRot.y))














