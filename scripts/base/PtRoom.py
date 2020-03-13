# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

class PtRoom(KBEngine.Space):
    """
    PtSpace的base部分，
    注意：它是一个实体，并不是真正的space，真正的space存在于cellapp的内存中，通过这个实体与之关联并操控space。
    """
    def __init__(self):
        KBEngine.Space.__init__(self)

        # 玩家字典, 保存该房间的玩家, key是实体ID,存放的是base实体, cell实体不考虑
        self.EntityDict = {}

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


    # ======引擎系统回调, 不修改方法大小写======
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

