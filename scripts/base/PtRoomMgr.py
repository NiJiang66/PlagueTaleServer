# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from ROOM_INFO import TRoomInfo, TRoomList
from PtRoom import PtRoom

class PtRoomMgr(KBEngine.Entity):
    """
    PtRoom的房间管理器
    """
    def __init__(self):
        KBEngine.Entity.__init__(self)

        # 存储在globalData中，方便获取
        KBEngine.globalData["PtRoomMgr"] = self

        # 存储所有的Room的base实体, 使用id作为下标,
        self.RoomList = {}

        # 创建中的房间字典, key : 房间名  value : Account
        self.DemandAccount = {}

        # 创建三个默认线路(也可以叫做房间或者地图)
        self.CreateRoom("线路-1", None)
        self.CreateRoom("线路-2", None)
        self.CreateRoom("线路-3", None)

    def CreateRoom(self, Name, Account):
        """
        # 创建房间
        # :param Name: 房间名
        # :param CallBack: 创建房间生成cell后的回调函数
        """
        # 查看是否有同名房间
        for RoomId, Room in self.RoomList.items():
            if Room.Name == Name:
                if Account is not None:
                    # 告诉账户以及有同名的房间
                    Account.OnAccountCreateRoom(False, 0, Name)
                return

        # 判断是否有正在创建中的同名的请求
        if Name in self.DemandAccount:
            Account.OnAccountCreateRoom(False, 0, Name)
            return

        if Account is not None:
            # 将请求创建的房间名和账户保存在正在创建字典中
            self.DemandAccount[Name] = Account

        # 创建房间
        Props = {
            "Name": Name
        }
        KBEngine.createEntityLocally("PtRoom", Props)

    def GetRoomList(self):
        """
        获取房间列表
        """
        RoomList = TRoomList()
        for RoomId, Room in self.RoomList.items():
            Props = {"RoomId" : RoomId, "Name" : Room.Name}
            RoomList[RoomId] = TRoomInfo().createFromDict(Props)
        return RoomList

    def GetRoomById(self, RoomId):
        """
        通过房间ID获取房间
        :param RoomId: 房间Id
        :return: 返回房间实体
        """
        if RoomId in self.RoomList:
            return self.RoomList[RoomId]
        return None

    def EnterRoom(self, EntityRole, RoomId):
        """
        角色选择进入id对应的房间
        :param EntityRole:角色id
        :param RoomId:房间id
        """
        # 根据空间id，得到对应Room实体
        Room = self.RoomList[RoomId]
        if Room is None:
            ERROR_MSG("PtRoomMgr::BaseEnterRoom: Room with Id(%i)  is none" % (RoomId))
            return
        Room.Enter(EntityRole)


    def LeaveRoom(self, EntityId, RoomId):
        """
        角色选择离开id对应的房间
        :param EntityId:角色id
        :param RoomId:房间id
        """
        # 根据空间id，得到对应Room实体
        Room = self.RoomList[RoomId]
        if Room is None:
            ERROR_MSG("PtRoomMgr::BaseLeaveRoom: Room with Id(%i)  is none" % (RoomId))
            return
        Room.Leave(EntityId)


    def OnRoomGetCell(self, Room):
        """
        创建房间cell实体生成回调函数
        :param Room: 创建出cell实体的房间的base实体
        """
        # 房间创建出cell实体之后才能添加到房间列表
        self.RoomList[Room.id] = Room

        for Name, Account in self.DemandAccount.items():
            if Name == Room.Name:
                # 告诉请求的账户创建房间成功
                Account.OnAccountCreateRoom(True, Room.id, Room.Name)
                # 删除账户
                del self.DemandAccount[Name]
                return



    def OnRoomLoseCell(self, RoomId):
        """
        创建房间cell实体生成回调函数
        :param RoomId: 房间id
        """
        del self.RoomList[RoomId]



