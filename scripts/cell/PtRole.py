# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.Character import Character

class PtRole(KBEngine.Entity,
             Character
             ):
	def __init__(self):
		KBEngine.Entity.__init__(self)