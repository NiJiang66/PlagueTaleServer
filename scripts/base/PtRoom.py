# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from CHAT_INFO import TChatInfo, TChatList
import time


class PtRoom(KBEngine.Space):
    """
    PtSpace的base部分，
    注意：它是一个实体，并不是真正的space，真正的space存在于cellapp的内存中，通过这个实体与之关联并操控space。
    """
    def __init__(self):
        KBEngine.Space.__init__(self)
        # 玩家字典, 保存该房间的玩家, key是实体ID,存放的是base实体, cell实体不考虑
        self.EntityDict = {}
        # 保存聊天信息的列表
        self.ChatList = []

    def Enter(self,EntityRole):
        """
        # 进入场景
        # :param EntityRole: 进入场景的Entity的Base实体
        """
        # 把实体放入房间的Cell空间 调用 self.cell.OnEnter(EntityRole) 也可以
        EntityRole.createCellEntity(self.cell)
        # 保存到玩家字典
        self.EntityDict[EntityRole.id] = EntityRole


    def Leave(self, EntityId):
        """
        # 离开场景, Base实体离开, 如果cell存在, 把对应cell删除
        """
        # 获取玩家
        EntityRole = self.EntityDict[EntityId]
        # 把玩家移出字典
        del self.EntityDict[EntityId]
        # 销毁玩家cell实体
        if EntityRole is not None:
            if EntityRole.cell is not None:
                EntityRole.destroyCellEntity()

    # =========聊天信息系统==============
    def AppendChatInfo(self, Name, Message):
        """
        添加一条聊天信息
        :param EntityRole: 发送信息的玩家
        :param Message:发送的信息
        """
        Props = {
            "Index"   : len(self.ChatList),
            "Name"    : Name,
            "Date"    : time.strftime("%H:%M:%S", time.localtime()),
            "Message" : Message
        }
        ChatInfo = TChatInfo().createFromDict(Props)
        self.ChatList.append(ChatInfo)

    def RequestChatList(self, EntityRole):
        """
        某玩家请求最新的聊天列表
        :param EntityRole:请求玩家
        return: 聊天信息列表 最新的聊天信息长度
        """
        # 提前获取当前信息数量
        ChatCount = len(self.ChatList)
        # 如果为0 说明是第一次请求聊天信息, 只允许发送20条以下的信息给玩家
        if EntityRole.ChatIndex is 0:
            if ChatCount > 20:
                return self.ChatList[ChatCount - 20: ChatCount], ChatCount
            else:
                return self.ChatList, ChatCount
        else:
            # 如果当前玩家信息序号大于等于信息数, 返回空列表和当前信息数, 这种情况应该不会出现
            if EntityRole.ChatIndex >= ChatCount:
                return [], ChatCount
            else:
                # 返回新的信息列表, 当前信息数
                return self.ChatList[EntityRole.ChatIndex: ChatCount], ChatCount


    # ======  引擎系统回调  ======

    def onGetCell(self):
        """
        # Room的cell部分被创建成功时就会回调该函数
        """
        #  通知RoomMgr，本房间已经创建完毕
        KBEngine.globalData["PtRoomMgr"].OnRoomGetCell(self)


    def onLoseCell(self):
        """
        # Room的cell部分实体丢失
        """
        #  通知RoomMgr，本房间已经销毁
        KBEngine.globalData["PtRoomMgr"].OnRoomLoseCell(self)
        self.destroy()

