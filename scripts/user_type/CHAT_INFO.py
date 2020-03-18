# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *


class TChatInfo(dict):
    def __init__(self):
        dict.__init__(self)

    def asDict(self):
        Data = {
            "Index": self["Index"],
            "Name": self["Name"],
            "Date": self["Date"],
            "Message": self["Message"]
        }
        return Data

    def createFromDict(self, DictData):
        self["Index"] = DictData["Index"]
        self["Name"] = DictData["Name"]
        self["Date"] = DictData["Date"]
        self["Message"] = DictData["Message"]
        return self


class CHAT_INFO_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dct):
        return TChatInfo().createFromDict(dct)

    def getDictFromObj(self, obj):
        return obj.asDict()

    def isSameType(self, obj):
        return isinstance(obj, TChatInfo)

ChatInfoInst = CHAT_INFO_PICKLER()


class TChatList(dict):
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
            Prop = {"Index": data["Index"], "Name": data["Name"], "Date": data["Date"], "Message": data["Message"]}
            self[data["Index"]] = ChatInfoInst.createObjFromDict(Prop)
        return self


class CHAT_LIST_PICKLER:
    def __init__(self):
        pass

    def createObjFromDict(self, dct):
        return TChatList().createFromDict(dct)

    def getDictFromObj(self, obj):
        return obj.asDict()

    def isSameType(self, obj):
        return isinstance(obj, TChatList)

ChatListInst = CHAT_LIST_PICKLER()

