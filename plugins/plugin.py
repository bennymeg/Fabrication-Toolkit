import os
import wx
import pcbnew # type: ignore

from .thread import ProcessThread
from .events import StatusEvent
from .options import EXCLUDE_DNP_OPT, AUTO_TRANSLATE_OPT, EXTRA_LAYERS
from .config import layers
from .utils import load_user_options, save_user_options


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

        userOptions = load_user_options({
            EXCLUDE_DNP_OPT: False,
            EXTRA_LAYERS: "",
            AUTO_TRANSLATE_OPT: True
        })

        self.mOptionsLabel = wx.StaticText(self, label='Options:')
        # self.mOptionsSeparator = wx.StaticLine(self)
        self.mAutomaticTranslation = wx.CheckBox(self, label='Apply automatic translations')
        self.mAutomaticTranslation.SetValue(userOptions[AUTO_TRANSLATE_OPT])
        self.mExcludeDnpCheckbox = wx.CheckBox(self, label='Exclude DNP components')
        self.mExcludeDnpCheckbox.SetValue(userOptions[EXCLUDE_DNP_OPT])

        self.mAdditionalLayersControl = wx.TextCtrl(self, size=wx.Size(600, 50))
        self.mAdditionalLayersControl.Hint = "Additional layers"
        self.mAdditionalLayersControl.AutoComplete(layers)
        self.mAdditionalLayersControl.Enable()
        self.mAdditionalLayersControl.SetValue(userOptions[EXTRA_LAYERS])

        self.mGenerateButton = wx.Button(self, label='Generate', size=wx.Size(600, 60))

        self.mGaugeStatus = wx.Gauge(
            self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size(600, 20), wx.GA_HORIZONTAL)
        self.mGaugeStatus.SetValue(0)
        self.mGaugeStatus.Hide()

        self.mGenerateButton.Bind(wx.EVT_BUTTON, self.onGenerateButtonClick)

        boxSizer = wx.BoxSizer(wx.VERTICAL)

        boxSizer.Add(self.mOptionsLabel, 0, wx.ALL, 5)
        # boxSizer.Add(self.mOptionsSeparator, 0, wx.ALL, 5)
        boxSizer.Add(self.mAdditionalLayersControl, 0, wx.ALL, 5)
        boxSizer.Add(self.mAutomaticTranslation, 0, wx.ALL, 5)
        boxSizer.Add(self.mExcludeDnpCheckbox, 0, wx.ALL, 5)
        boxSizer.Add(self.mGaugeStatus, 0, wx.ALL, 5)
        boxSizer.Add(self.mGenerateButton, 0, wx.ALL, 5)

        self.SetSizer(boxSizer)
        self.Layout()
        boxSizer.Fit(self)

        self.Centre(wx.BOTH)


    def onGenerateButtonClick(self, event):
        options = dict()
        options[AUTO_TRANSLATE_OPT] = self.mAutomaticTranslation.GetValue()
        options[EXCLUDE_DNP_OPT] = self.mExcludeDnpCheckbox.GetValue()
        options[EXTRA_LAYERS] = self.mAdditionalLayersControl.GetValue()

        save_user_options(options)

        self.mAdditionalLayersControl.Hide()
        self.mAutomaticTranslation.Hide()
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
