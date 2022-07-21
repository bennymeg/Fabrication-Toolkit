import wx

STATUS_EVENT_ID = wx.NewId()


class StatusEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(STATUS_EVENT_ID)
        self.data = data

    @staticmethod
    def invoke(window, function):
        window.Connect(-1, -1, STATUS_EVENT_ID, function)
