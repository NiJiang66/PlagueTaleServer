# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from ROLE_DATA import TRoleData
from ROLE_INFO import TRoleInfo,TRoleList
from ROOM_INFO import TRoomInfo,TRoomList
from BAG_INFO import TGoodInfo, TBagInfo
from D_Good import *


class PtAccount(KBEngine.Proxy):
	def __init__(self):
		KBEngine.Proxy.__init__(self)
		self.ActiveRole = None

	def onTimer(self, id, userArg):
		"""
		KBEngine method.
		使用addTimer后， 当时间到达则该接口被调用
		@param id		: addTimer 的返回值ID
		@param userArg	: addTimer 最后一个参数所给入的数据
		"""
		DEBUG_MSG(id, userArg)
		
	def onClientEnabled(self):
		"""
		KBEngine method.
		该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
		cell部分。
		"""
		INFO_MSG("PtAccount[%i] entities enable. entityCall:%s" % (self.id, self.client))
			
	def onLogOnAttempt(self, ip, port, password):
		"""
		KBEngine method.
		客户端登陆失败时会回调到这里
		"""
		INFO_MSG(ip, port, password)
		return KBEngine.LOG_ON_ACCEPT
		
	def onClientDeath(self):
		"""
		KBEngine method.
		客户端对应实体已经销毁
		"""
		DEBUG_MSG("PtAccount[%i].onClientDeath:" % self.id)
		self.destroy()


	def ReqRoleList(self):
		"""
        客户端请求角色列表
        """
		DEBUG_MSG("PtAccount[%i].ReqRoleList: Size=%i. Data = %s" % (self.id, len(self.RoleList), self.RoleList))

		# 在这个位置判断已激活角色是否为空, 如果不为空, 说明是从房间返回到大厅, base实体还存在, 直接销毁
		if self.ActiveRole is not None:
			self.ActiveRole.destroy()
			self.ActiveRole = None

		# 再发送角色列表到客户端
		self.client.OnReqRoleList(self.RoleList)

	def ReqCreateRole(self, RoleType, Name):
		"""
        客户端请求创建一个角色
        """
		# 先创建空的RoleInfo角色信息类，用来给创建角色失败时作为创建角色回调函数的参数
		RoleInfo = TRoleInfo()
		RoleInfo.extend([0, Name, RoleType, TRoleData().createFromDict({"DataType": 0, "DataValue": b''})])

		# 检查是否能够创建角色，依据是是否有同名或者同类型的角色存在
		for key,info in self.RoleList.items():
			if info[1] is Name:
				if self.client:
					self.client.OnCreateRoleResult(1, RoleInfo)
					return
			if info[2] is RoleType:
				if self.client:
					self.client.OnCreateRoleResult(2, RoleInfo)
					return

		#获取场景并且声称角色，将角色写到数据库，数据库写入完成后再告诉客户端创建结果，第一次创建的角色要给初始技能,暂时只做了1个技能，并且先放到主背包
		SkillBagProp = {"Value":[]}
		#for Index in range(0,1):
		#	SkillGoodProp = {
		#		"BlockId": Index,
		#		"GoodId": GetGoodIdByTypeKind(EGoodType.Skill.value, Index),
		#		"Number": 1,
		#	}
		#	SkillBagProp["Value"].append(TGoodInfo().createFromDict(SkillGoodProp))
		SkillBag = TBagInfo().createFromDict(SkillBagProp)

		# 这里把所有的物品都创建出来放到主背包作为测试用, 技能除外
		# 装备物品
		MainBagProp = {"Value": []}


		for Index in range(0, 3):
			EquipGoodProp = {
				"BlockId": Index,
				"GoodId": GetGoodIdByTypeKind(EGoodType.Equip.value, Index),
				"Number": 1,
			}
			MainBagProp["Value"].append(TGoodInfo().createFromDict(EquipGoodProp))

		# buff物品
		for Index in range(0, 3):
			BuffGoodProp = {
				"BlockId": Index + 3,
				"GoodId": GetGoodIdByTypeKind(EGoodType.Buff.value, Index),
				"Number": 20,
			}
			MainBagProp["Value"].append(TGoodInfo().createFromDict(BuffGoodProp))

		for Index in range(0,1):
			SkillGoodProp = {
				"BlockId": Index + 6,
				"GoodId": GetGoodIdByTypeKind(EGoodType.Skill.value, Index),
				"Number": 1,
			}
			MainBagProp["Value"].append(TGoodInfo().createFromDict(SkillGoodProp))

		MainBag = TBagInfo().createFromDict(MainBagProp)

		# 创建PtRole
		Props = {
			"Name" 		: Name,
			"RoleType"	: RoleType,
			"SkillBag"	: SkillBag,
			"MainBag"	: MainBag
		}
		Role = KBEngine.createEntityLocally("PtRole", Props)

		# 将角色写入数据库，再在回调函数通知客户端是否创建角色成功
		if Role:
			Role.writeToDB(self._OnRoleSaved)

	def _OnRoleSaved(self, Success, Role):
		"""
		新建角色写入数据库回到
		:param Success: 是否写入成功
		:param Role: 写入数据库的实体
		"""
		INFO_MSG('PtAccount::_OnRoleSaved:(%i) create role state: %i, %s, %i' % (
		self.id, Success, Role.cellData["Name"], Role.databaseID))

		# 检查账号是否已经销毁,若正在销毁无法写入，则从数据库删除该角色实体数据
		if self.isDestroyed:
			if Role:
				Role.destroy(True)
				return

		RoleInfo = TRoleInfo()
		RoleInfo.extend([0, "", 0, TRoleData().createFromDict({"DataType": 0, "DataValue": b''})])

		if Success:
			TargetInfo = TRoleInfo()
			TargetInfo.extend([Role.databaseID, Role.cellData["Name"], Role.cellData["RoleType"],
							   TRoleData().createFromDict({"DataType": 1, "DataValue": b'1'})])
			self.RoleList[Role.databaseID] = TargetInfo
			RoleInfo[0] = Role.databaseID
			# cellData可以获取未生成cell作用域的变量
			RoleInfo[1] = Role.cellData["Name"]
			RoleInfo[2] = Role.cellData["RoleType"]
			RoleInfo[3] = TRoleData().createFromDict({"DataType": 1, "DataValue": b'1'})
			# 马上保存新角色到数据库
			self.writeToDB()
		else:
			RoleInfo[1] = "创建失败"

		Role.destroy()

		if self.client:
			self.client.OnCreateRoleResult(0, RoleInfo)



	def ReqRemoveRole(self, Name):
		"""
        客户端请求删除一个角色,此处使用角色名来选择，可能不太严谨，之后可以增加或修改为根据ID来选择
        """
		DEBUG_MSG("PtAccount[%i].ReqRemoveRole: %s" % (self.id, Name))

		# 数据库Id
		Dbid = -1

		for key, info in self.RoleList.items():
			# 如果角色存在, 保存key到数据库Id
			if info[1] == Name:
				Dbid = key
				break

		# 如果Dbid为负, 说明不存在对应角色, 直接返回
		if Dbid == -1:
			return

		# 从数据库生成该角色, 生成该角色后，再调用该角色的destroy(True)从数据库删除
		KBEngine.createEntityFromDBID("PtRole", Dbid, self._OnRoleRemoved)

	def _OnRoleRemoved(self, BaseRef, Dbid, WasActive):
		"""
        删除角色回调函数(情况为“进入游戏时从数据库创建出角色”时的方法)
        :param BaseRef:角色实体的直接引用
        :param Dbid:实体数据库Id
        :param WasActive:是否激活，如果True说明该实体已经存在
        """
		if WasActive:
			ERROR_MSG("PtAccount::_OnRoleRemoved:(%i): this role is in world now!" % (self.id))
			return

		if BaseRef is None:
			ERROR_MSG("PtAccount::_OnRoleRemoved:(%i): the role you wanted to created from DB is not exist!" % (self.id))
			return

		# 获取角色实体
		Role = KBEngine.entities.get(BaseRef.id)

		if Role is None:
			ERROR_MSG("PtAccount::_OnRoleRemoved:(%i): when role was created, it died as well!" % (self.id))
			return

		# 获取角色数据库id
		#Dbid = Role.databaseID
		# 如果Role存在, 从数据库删除
		Role.destroy(True)

		# 告诉客户端删除角色
		self.client.OnRemoveRole(Dbid)

		# 从角色列表移除
		del self.RoleList[Dbid]
		# 更新角色列表到数据库
		self.writeToDB()

	def ReqSelectRoleGame(self, Dbid):
		"""
        客户端选择某个角色进行游戏
        """
		# DEBUG_MSG("PtAccount[%i].SelectRoleGame:%i" % (self.id, Dbid))
		# 判断该数据库Id是否存在对应角色
		if Dbid in self.RoleList:
			# 把传过来的Dbid保存到LastSelRole本地变量
			self.LastSelRole = Dbid
			# 回调客户端的选择角色
			self.client.OnSelectRoleGame(0, Dbid)
		else:
			DEBUG_MSG("PtAccount[%i].SelectRoleGame:%i. No Dbid = %i" % (self.id, Dbid))
			# 回调客户端的选择角色
			self.client.OnSelectRoleGame(1, Dbid)

	def ReqRoomList(self):
		"""
		请求房间列表
		"""
		RoomList = KBEngine.globalData["PtRoomMgr"].GetRoomList()
		DEBUG_MSG("PtAccount[%i].ReqRoomList: RoomList = %s" % (self.id, RoomList.asDict()))
		self.client.OnReqRoomList(RoomList)

	def ReqCreateRoom(self, Name):
		"""
		请求创建房间,创建房间后调用self.OnAccountCreateRoom
		:param Name: 房间名字
		"""
		DEBUG_MSG("PtAccount[%i].ReqCreateRoom: RoomName = %s" % (self.id, Name))
		KBEngine.globalData["PtRoomMgr"].CreateRoom(Name, self)

	def OnAccountCreateRoom(self, Succeed, RoomId, Name):
		"""
		创建房间回调函数
		:param Succeed: 是否成功
		:param RoomId: 房间id
		:param Name: 房间Name
		"""
		Props = {"RoomId": RoomId, "Name": Name}
		RoomInfo = TRoomInfo().createFromDict(Props)

		if Succeed:
			self.client.OnCreateRoom(0, RoomInfo)
		else:
			self.client.OnCreateRoom(1, RoomInfo)

	def SelectRoomGame(self, RoomId):
		'''
		选择房间进入游戏
		:param RoomId: 房间id
		'''
		DEBUG_MSG("PtAccount[%i].SelectRoomGame: RoomId = %i , RoleId = %i" % (self.id, RoomId, self.LastSelRole))
		# 保存房间id
		self.LastSelRoom = RoomId
		# 从数据库创建选中的角色
		KBEngine.createEntityFromDBID("PtRole", self.LastSelRole, self._OnRoleCreated)

	def _OnRoleCreated(self, BaseRef, Dbid, WasActive):
		"""
		选择房间进入游戏从数据库创建选中的角色的回调函数
		:param BaseRef:角色实体的直接引用
		:param Dbid:数据库id
		:param WasActive:是否已经存在于世界，是否激活
		"""
		if WasActive:
			ERROR_MSG("PtAccount[%i]::_OnRoleCreated: this role is in world" % self.id)
			return

		if BaseRef is None:
			ERROR_MSG("PtAccount[%i]::_OnRoleCreated: this role create from DB is not Exit" % self.id)
			return

		# 获取角色实体
		Role = KBEngine.entities.get(BaseRef.id)

		if Role is None:
			ERROR_MSG("PtAccount[%i]::_OnRoleCreated: when role was created, it died as well!" % self.id)
			return

		if self.isDestroyed:
			ERROR_MSG("PtAccount::_OnRoleCreated:(%i): i dead, will the destroy of role!" % (self.id))
			Role.destroy()
			return

		DEBUG_MSG('PtAccount::_OnRoleCreated:(%i) enter room game:  %s, %i' % (self.id, Role.cellData["Name"], Role.databaseID))

		# 保存角色实体到本地
		self.ActiveRole = Role
		# 移交客户端代理到角色，移交客户端代理之后，服务端的Account实体不会销毁，
		# 但是客户端的Account实体会销毁，同时客户端只能和Role角色实体进行联网交互。
		# 如非要与Account实体交互，需要在服务端将Role上的客户端代理移交回Account实体
		self.giveClientTo(Role)
		# 保存Account实体到Role
		Role.AccountEntity = self
		# 角色进入场景
		KBEngine.globalData["PtRoomMgr"].EnterRoom(Role,self.LastSelRoom)







