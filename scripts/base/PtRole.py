# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

class PtRole(KBEngine.Proxy):
	def __init__(self):
		KBEngine.Proxy.__init__(self)
		# 保存账户实体
		self.AccountEntity = None