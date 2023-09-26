import os
import wx
import pcbnew  # type: ignore

from .thread import ProcessThread
from .events import StatusEvent
from .options import EXCLUDE_DNP_OPT


# WX GUI form that show the plugin progress
class KiCadToJLCForm(wx.Frame):
    def __init__(self):
        wx.Dialog.__init__(
            self,
            None,
            id=wx.ID_ANY,
            title=u"Fabrication Toolkit",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.DEFAULT_DIALOG_STYLE)
        
        # self.app = wx.PySimpleApp()
        icon = wx.Icon(os.path.join(os.path.dirname(__file__), 'icon.png'))
        self.SetIcon(icon)
        self.SetBackgroundColour(wx.LIGHT_GREY)

        self.SetSizeHints(wx.Size(600, 100), wx.DefaultSize)

        self.mOptionsLabel = wx.StaticText(self, label='Options:')
        # self.mOptionsSeparator = wx.StaticLine(self)
        self.mExcludeDnpCheckbox = wx.CheckBox(self, label='Exclude DNP components')
        self.mExcludeDnpCheckbox.SetValue(False)

        self.mGenerateButton = wx.Button(self, label='Generate', size=wx.Size(600, 60))

        self.mGaugeStatus = wx.Gauge(
            self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size(600, 20), wx.GA_HORIZONTAL)
        self.mGaugeStatus.SetValue(0)
        self.mGaugeStatus.Hide()

        self.mGenerateButton.Bind(wx.EVT_BUTTON, self.onGenerateButtonClick)

        boxSizer = wx.BoxSizer(wx.VERTICAL)

        boxSizer.Add(self.mOptionsLabel, 0, wx.ALL, 5)
        # boxSizer.Add(self.mOptionsSeparator, 0, wx.ALL, 5)
        boxSizer.Add(self.mExcludeDnpCheckbox, 0, wx.ALL, 5)
        boxSizer.Add(self.mGaugeStatus, 0, wx.ALL, 5)
        boxSizer.Add(self.mGenerateButton, 0, wx.ALL, 5)

        self.SetSizer(boxSizer)
        self.Layout()
        boxSizer.Fit(self)

        self.Centre(wx.BOTH)


    def onGenerateButtonClick(self, event):
        options = dict()
        options[EXCLUDE_DNP_OPT] = self.mExcludeDnpCheckbox.GetValue()

        self.mExcludeDnpCheckbox.Hide()
        self.mOptionsLabel.Hide()
        self.mGenerateButton.Hide()
        self.mGaugeStatus.Show()

        self.Fit()
        self.SetTitle('Fabrication Toolkit (Processing...)')

        StatusEvent.invoke(self, self.updateDisplay)
        ProcessThread(self, options)

    def updateDisplay(self, status):
        if status.data == -1:
            self.SetTitle('Fabrication Toolkit (Done!)')
            pcbnew.Refresh()
            self.Destroy()
        else:
            self.mGaugeStatus.SetValue(int(status.data))


# Plugin definition
class Plugin(pcbnew.ActionPlugin):
    def __init__(self):
        self.name = "Fabrication Toolkit"
        self.category = "Manufacturing"
        self.description = "Toolkit for automating PCB fabrication process with KiCad and JLC PCB"
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.dark_icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def Run(self):
        KiCadToJLCForm().Show()
