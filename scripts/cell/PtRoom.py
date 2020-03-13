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

        KBEngine.addSpaceGeometryMapping(self.spaceID, None, "spaces/MmoMapOne")
        # KBEngine.addSpaceGeometryMapping(self.spaceID, None, "spaces/MmoMapTwo")