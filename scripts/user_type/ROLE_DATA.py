# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

class TRoleData(dict):

    def __init__(self):
        dict.__init__(self)

    def asDict(self):
        return {"DataType":self["DataType"],"DataValue":self["DataValue"]}

    def createFromDict(self, DictData):
        self["DataType"] = DictData["DataType"]
        self["DataValue"] = DictData["DataValue"]
        return self


class ROLE_DATA_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dict):
        return TRoleData().createFromDict(dict)

    def getDictFromObj(self, obj):
        return obj.asDict()

    def isSameType(self, obj):
        return isinstance(obj, TRoleData)

RoleDataPickler = ROLE_DATA_PICKLER()