# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *



class TGoodInfo(dict):
    def __init__(self):
        dict.__init__(self)

    def asDict(self):
        Data = {
            "BlockId"  : self["BlockId"],
            "GoodId" : self["GoodId"],
            "Number" : self["Number"]
        }
        return Data

    def createFromDict(self, DictData):
        # self.extend([DictData["BlockId"], DictData["GoodId"], DictData["Number"])
        self["BlockId"] = DictData["BlockId"]
        self["GoodId"] = DictData["GoodId"]
        self["Number"] = DictData["Number"]
        return self

class GOOD_INFO_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dct):
        return TGoodInfo().createFromDict(dct)

    def getDictFromObj(self, obj):
        return obj.asDict()

    def isSameType(self, obj):
        return isinstance(obj, TGoodInfo)


GoodInfoInst = GOOD_INFO_PICKLER()

class TBagInfo(dict):
    def __init__(self):
        dict.__init__(self)

    def asDict(self):
        Data = []

        for key, val in self.items():
            Data.append(val)

        Dict = {"Value": Data}

        return Dict


    def createFromDict(self, DictData):
        for data in DictData["Value"]:
            Prop = {"BlockId" : data["BlockId"], "GoodId" : data["GoodId"], "Number" : data["Number"]}
            self[data["BlockId"]] = GoodInfoInst.createObjFromDict(Prop)
        return self


class BAG_INFO_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dct):
        return TBagInfo().createFromDict(dct)

    def getDictFromObj(self, obj):
        return obj.asDict()

    def isSameType(self, obj):
        return isinstance(obj, TBagInfo)


BagInfoInst = BAG_INFO_PICKLER()









