import wx

EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
