from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify import DirectNotifyGlobal
from toontown.chat.ChatGlobals import *

class ChatAgentAI(DistributedObjectGlobalAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("ChatAgentAI")

    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)

    def chatMessageResponse(self, sender, message):
        if sender not in self.air.doId2do.keys():
            # found an invalid sender!
            return

        av = self.air.doId2do[sender]

        if not av:
            # got a invalid avatar object!
            return

        # broadcast chat message update
        av.sendUpdate('setChat', [message, CFSpeech | CFQuicktalker | CFTimeout])