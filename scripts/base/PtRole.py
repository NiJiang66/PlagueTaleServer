# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import random
import Math
from BAG_INFO import TGoodInfo, TBagInfo
from D_Good import *

class PtRole(KBEngine.Proxy):
	def __init__(self):
		KBEngine.Proxy.__init__(self)
		# 保存账户实体
		self.AccountEntity = None

		# 生成初始化位置
		self.cellData["SpawnPoint"] = Math.Vector3(random.randint(2500, 5000), random.randint(2500, 5000), 10)


	def ReqBagList(self):
		"""
        客户端请求所有背包数据
        """
		self.client.OnReqBagList(self.MainBag, self.SkillBag, self.BuffBag, self.EquipBag)

	def IncreaseGood(self, GoodId, GoodType):
		"""
        填加物品到背包
        :param GoodId: 物品Id
        :param GoodType: 物品类型
        """
		# 区分类型填充到对应背包, 装备背包不考虑
		if GoodType is EGoodType.Skill.value:
			# 遍历技能背包, 如果技能背包里有对应技能, 不进行添加，直接返回
			for key, info in self.SkillBag.items():
				if info["GoodId"] is GoodId:
					# 如果技能物品id对应，不添加数量，技能不允许添加数量，直接返回结果
					self.client.OnIncreaseGood(EBagType.SkillBag.value, info)
					return
			#游戏暂不将技能作为物品拾取，而是设定每种角色都有自己的初始技能
			return
		elif GoodType is EGoodType.Buff.value:
			# 遍历Buff背包, 如果没有对应Buff, 直接把Buff放到主背包
			for key, info in self.BuffBag.items():
				if info["GoodId"] is GoodId:
					# 如果物品Id对应
					info["Number"] = min(info["Number"] + GoodDatas[GoodId]["Number"], 99)
					# 告诉客户端添加了物体
					self.client.OnIncreaseGood(EBagType.BuffBag.value, info)
					return
		elif GoodType is EGoodType.Equip.value:
			# 查看装备背包里是否已经有对应物体, 如果有的话不进行物品的添加, 直接返回
			for key, info in self.EquipBag.items():
				if info["GoodId"] is GoodId:
					# 如果装备物品Id对应, 不添加数量, 装备不允许添加数量, 直接返回结果
					self.client.OnIncreaseGood(EBagType.EquipBag.value, info)
					# 直接返回
					return

		# 如果上面的步骤添加物品都不成功, 把物品添加到主背包, 主背包有9格

		# 保存空格子Id
		EmptyId = 0
		for key, info in self.MainBag.items():
			# 空格子Id + 1, 如果最后不是9, 说明EmptyId背包格是空的
			if EmptyId is key:
				EmptyId += 1
			# 判断是否有同Id
			if info["GoodId"] is GoodId:
				# 装备物品数量 + 0, 这里不另外判断
				info["Number"] = min(info["Number"] + GoodDatas[GoodId]["Number"], 99)
				# 告诉客户端添加了物体
				self.client.OnIncreaseGood(EBagType.MainBag.value, info)
				return

		# 运行到这里说明需要将物品添加到空格子
		# 如果空格子为9, 说明没有格子可用
		if EmptyId is 9:
			return

		# 创建新的物品格子
		Props = {
			"BlockId": EmptyId,
			"GoodId": GoodId,
			"Number": GoodDatas[GoodId]["Number"]
		}
		GoodInfo = TGoodInfo().createFromDict(Props)
		# 填充物品到主背包
		self.MainBag[EmptyId] = GoodInfo

		# 告诉客户端添加物品
		self.client.OnIncreaseGood(EBagType.MainBag.value, GoodInfo)

	def ReduceGood(self, BagType, BlockId):
		"""
        告知服务端使用物品, 使用减少仅限于Buff
        :param BagType: 背包类型
        :param GoodInfo: 物品
        """
		# 定义变量判定是否无背包数据
		IsEmptyBlockId = False

		if BagType is EBagType.BuffBag.value:
			# 从Buff背包减少物品
			if BlockId in self.BuffBag:
				self.BuffBag[BlockId]["Number"] -= 1
				# 告诉客户端减少物品
				self.client.OnReduceGood(EReduceResult.Succeed.value, BagType, self.BuffBag[BlockId])
				# 获取细分种类Id
				KindId = GetKindIdByGoodId(self.BuffBag[BlockId]["GoodId"])
				# 告诉cell实体添加Buff
				self.cell.AddBuff(KindId)
				# 如果数量已经为0, 删除该物品
				if self.BuffBag[BlockId]["Number"] is 0:
					del self.BuffBag[BlockId]
			else:
				IsEmptyBlockId = True
		# 如果都不在这个背包里, 强制清空客户端背包
		else:
			IsEmptyBlockId = True

		if IsEmptyBlockId:
			# 如果传过来的物品不存在背包内, 返回空物品, 让客户端清除该物品
			Props = {
				"BlockId": 0,
				"GoodId": 0,
				"Number": 0
			}
			self.client.OnReduceGood(EReduceResult.NoGood.value, BagType, TGoodInfo().createFromDict(Props))

	def PassGood(self, ArcBagType, ArcBlockId, DesBagType, DesBlockId):
		"""
        背包物品移动
        :param ArcBagType:移出背包类型
        :param ArcBlockId:移出背包格子
        :param DesBagType:移入背包类型
        :param DesBlockId:移入背包格子
        """
		# 先生成两个空背包格子, 填入格子的BlockId, 返回空背包数据时就使用这两个数据
		ArcEmptyProps = {
			"BlockId": ArcBlockId,
			"GoodId": 0,
			"Number": 0
		}
		ArcEmptyGoodInfo = TGoodInfo().createFromDict(ArcEmptyProps)

		DesEmptyProps = {
			"BlockId": DesBlockId,
			"GoodId": 0,
			"Number": 0
		}
		DesEmptyGoodInfo = TGoodInfo().createFromDict(DesEmptyProps)

		# 获取背包物品
		ArcGoodInfo = self.GetGoodInfo(ArcBagType, ArcBlockId)

		# 如果移出物品为空
		if ArcGoodInfo is None:
			# 告诉客户端移入物品不存在
			self.client.OnPassGood(ArcBagType, ArcEmptyGoodInfo, DesBagType, DesEmptyGoodInfo)
			return

		# 如果移出物品存在，获取移入背包物品
		DesGoodInfo = self.GetGoodInfo(DesBagType, DesBlockId)

		# 如果移入背包格子不为空
		if DesGoodInfo is not None:
			# 告诉客户端目标格子有物品
			self.client.OnPassGood(ArcBagType, ArcGoodInfo, DesBagType, DesGoodInfo)
			return

		# 获取存入物品的物品类型
		ArcGoodType = GetTypeByGoodId(ArcGoodInfo["GoodId"])
		# 获取存入物品的细分类型Id
		ArcKindId = GetKindIdByGoodId(ArcGoodInfo["GoodId"])

		# 判定是否物品与格子是否匹配, Skill部分
		if DesBagType is EBagType.SkillBag.value and ArcGoodType is not EGoodType.Skill.value:
			self.client.OnPassGood(ArcBagType, ArcGoodInfo, DesBagType, DesEmptyGoodInfo)
			return
		"""
        添加技能的话应该直接装入物品就行
        elif DesBagType is EBagType.SkillBag.value and ArcGoodType is EGoodType.Skill.value:
            # 处理填充技能逻辑
            return
        """

		# 判定是否物品与格子是否匹配, Buff部分
		if DesBagType is EBagType.BuffBag.value and ArcGoodType is not EGoodType.Buff.value:
			self.client.OnPassGood(ArcBagType, ArcGoodInfo, DesBagType, DesEmptyGoodInfo)
			return
		"""
        添加Buff的话应该直接装入物品就行
        elif DesBagType is EBagType.BuffBag.value and ArcGoodType is EGoodType.Buff.value:
            # 处理添加Buff逻辑
            return
        """

		# 判定物品与格子是否匹配, Equip部分, 三个格子不能乱放
		if DesBagType is EBagType.EquipBag.value and ArcGoodType is not EGoodType.Equip.value:
			self.client.OnPassGood(ArcBagType, ArcGoodInfo, DesBagType, DesEmptyGoodInfo)
			return
		elif DesBagType is EBagType.EquipBag.value and ArcGoodType is EGoodType.Equip.value:
			# 判断装备格子是否匹配, 通过装备物品的细分类型Id和目标格子Id对比来判断
			if ArcKindId is not DesBlockId:
				self.client.OnPassGood(ArcBagType, ArcGoodInfo, DesBagType, DesEmptyGoodInfo)
				return
			else:
				# 告诉cell穿上装备
				self.cell.PutOnEquip(ArcKindId)

		# 判断原背包是否是装备背包, 如果是装备背包要告诉cell脱掉装备
		if ArcBagType is EBagType.EquipBag.value:
			self.cell.TakeOffEquip(ArcKindId)

		# 把物品从原格子移出
		del self.GetBagByType(ArcBagType)[ArcBlockId]
		# 修改物品的格子为DesBlockId
		ArcGoodInfo["BlockId"] = DesBlockId
		# 把物品移入目标格子
		self.PutGoodToBag(DesBagType, DesBlockId, ArcGoodInfo)

		# 告诉客户端转移物品成功
		self.client.OnPassGood(ArcBagType, ArcEmptyGoodInfo, DesBagType, ArcGoodInfo)

	def GetBagByType(self, BagType):
		"""
        根据背包类型返回对应背包
        :param BagType:背包类型
        :return:返回背包
        """
		if BagType is EBagType.MainBag.value:
			return self.MainBag
		elif BagType is EBagType.SkillBag.value:
			return self.SkillBag
		elif BagType is EBagType.BuffBag.value:
			return self.BuffBag
		elif BagType is EBagType.EquipBag.value:
			return self.EquipBag
		return None

	def GetGoodInfo(self, BagType, BlockId):
		"""
        获取某个背包的某个格子的物品
        :param BagType:
        :param BlockId:
        :return:返回物品
        """
		Bag = self.GetBagByType(BagType)
		if Bag is None:
			return None

		if BlockId in Bag:
			return Bag[BlockId]

		return None

	def PutGoodToBag(self, BagType, BlockId, GoodInfo):
		"""
        将物品添加到背包
        :param BagType:
        :param BlockId:
        :param GoodInfo:
        """
		if BagType is EBagType.SkillBag.value:
			self.SkillBag[BlockId] = GoodInfo
		elif BagType is EBagType.BuffBag.value:
			self.BuffBag[BlockId] = GoodInfo
		elif BagType is EBagType.EquipBag.value:
			self.EquipBag[BlockId] = GoodInfo
		elif BagType is EBagType.MainBag.value:
			self.MainBag[BlockId] = GoodInfo
