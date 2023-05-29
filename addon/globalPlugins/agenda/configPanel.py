# -*- coding: UTF-8 -*-
# Module for Agenda add-on settings panel
# written by Abel Passos do Nascimento Jr. <abel.passos@gmail.com>, Rui Fontes <rui.fontes@tiflotecnia.com> and Ângelo Abrantes <ampa4374@gmail.com> and 
# Copyright (C) 2022-2023 Abel Passos Jr. and Rui Fontes
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

# Import the necessary modules
import os
import gui
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from gui import guiHelper
import wx
import globalVars
import config
from configobj import ConfigObj
import addonHandler

# To start the translation process
addonHandler.initTranslation()

# Constants
dirDatabase = os.path.join(os.path.dirname(__file__), "agenda.db")

def initConfiguration():
	confspec = {
		"show" : "boolean(default=True)",
		"days" : "integer(1, 30, default=1)",
		"path" : "string(default="")",
		"altPath" : "string(default="")",
		"xx" : "string(default="")",
	}
	config.conf.spec["agenda"] = confspec

initConfiguration()

# Read configuration on INI file to know how many days to include in next events
global nDays
nDays = 2
try:
	if config.conf["agenda"]["days"]:
		# Number of days to include in next events
		nDays = int(config.conf["agenda"]["days"])
except:
	pass

# Read configuration on INI file to know where are the agenda.db files...
dirDatabase = os.path.join(os.path.dirname(__file__), "agenda.db")
firstDatabase = ""
altDatabase = ""
indexDB = 0

try:
	if config.conf["agenda"]["xx"]:
		# index of agenda.db file to use
		indexDB = int(config.conf["agenda"]["xx"])
		if indexDB == 0:
			dirDatabase = 				config.conf["agenda"]["path"]
		else:
			dirDatabase = 				config.conf["agenda"]["altPath"]
		firstDatabase = config.conf["agenda"]["path"]
		altDatabase = config.conf["agenda"]["altPath"]
except:
	# Not registered, so use the default path
	pass


class AgendaSettingsPanel(gui.SettingsPanel):
	# Translators: Title of the Agenda settings dialog in the NVDA settings.
	title = _("Agenda")

	def makeSettings(self, settingsSizer):
		settingsSizerHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		# Translators: Checkbox name in the configuration dialog
		self.showNextAppointmentsWnd = wx.CheckBox(self, label = _("Show next appointments at startup"))
		self.showNextAppointmentsWnd.SetValue(bool(config.conf["agenda"]["show"]))
		settingsSizerHelper.addItem(self.showNextAppointmentsWnd)

		label_1 = wx.StaticText(self, wx.ID_ANY, _("Number of days in next events:"))
		settingsSizerHelper.addItem(label_1)
		# Translators: EditComboBox name in the configuration dialog to set the number of days included in the events notification
		self.days = wx.SpinCtrl(self, wx.ID_ANY, "1", min=1, max=30)
		self.days .SetValue(config.conf["agenda"]["days"])
		settingsSizerHelper.addItem(self.days)

		# Translators: Name of combobox with the agenda files path
		pathBoxSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label = _("Path of agenda files:"))
		pathBox = pathBoxSizer.GetStaticBox()
		pathGroup = guiHelper.BoxSizerHelper(self, sizer = pathBoxSizer)
		settingsSizerHelper.addItem(pathGroup)

		global firstDatabase
		if firstDatabase == "":
			firstDatabase = dirDatabase
		self.pathList = [firstDatabase, altDatabase]
		self.pathNameCB = pathGroup.addLabeledControl("", wx.Choice, choices = self.pathList)
		self.pathNameCB.SetSelection(indexDB)

		# Translators: This is the label for the button used to add or change a agenda.db location
		changePathBtn = wx.Button(pathBox, label = _("&Select or add a directory"))
		changePathBtn.Bind(wx.EVT_BUTTON,self.OnDirectory)

	def OnDirectory(self, event):
		self.Freeze()
		global dirDatabase, firstDatabase, altDatabase, indexDB
		lastDir = os.path.dirname(__file__)
		dDir = lastDir
		dFile = "agenda.db"
		frame = wx.Frame(None, -1, 'teste')
		frame.SetSize(0,0,200,50)
		dlg = wx.FileDialog(frame, _("Choose where to save the agenda file"), dDir, dFile,
				wildcard = _("Database files (*.db)"),
				style = wx.FD_SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			fname = dlg.GetPath()
			index = self.pathNameCB.GetSelection()
			if index == 0:
				if os.path.exists(fname):
					firstDatabase = fname
				else:
					os.rename(firstDatabase, fname)
					firstDatabase = fname
			else:
				if os.path.exists(fname):
					altDatabase = fname
				else:
					if altDatabase == "":
						altDatabase = fname
					else:
						os.rename(altDatabase, fname)
						altDatabase = fname
			dirDatabase = fname
			self.pathList = [firstDatabase, altDatabase]
		dlg.Close() 
		self.onPanelActivated()
		self._sendLayoutUpdatedEvent()
		self.Thaw()
		event.Skip()

	def onSave (self):
		global dirDatabase, indexDB, days
		config.conf["agenda"]["show"] = self.showNextAppointmentsWnd.GetValue()
		config.conf["agenda"]["days"] = self.days.GetValue()
		config.conf["agenda"]["path"] = firstDatabase
		config.conf["agenda"]["altPath"] = altDatabase
		config.conf["agenda"]["xx"] = str(self.pathList.index(self.pathNameCB.GetStringSelection()))
		indexDB = self.pathNameCB.GetSelection()
		dirDatabase = self.pathList[indexDB]

	def onPanelActivated(self):
		# Deactivate all profile triggers and active profiles
		config.conf.disableProfileTriggers()
		self.Show()

	def onPanelDeactivated(self):
		# Reactivate profiles triggers
		config.conf.enableProfileTriggers()
		self.Hide()

	def terminate(self):
		super(AgendaSettingsPanel, self).terminate()
		pass

