#-*- coding: utf-8 -*-
# Part of frequentText add-on for NVDA.
# written by Rui Fontes <rui.fontes@tiflotecnia.com> and Ângelo Abrantes

import os
import globalVars
import addonHandler

def onInstall():
	configFilePath = os.path.abspath(os.path.join(globalVars.appArgs.configPath, "addons", "agenda", "globalPlugins", "agenda", "agenda.db"))
	if os.path.isfile(configFilePath):	
		os.rename(configFilePath, os.path.abspath(os.path.join(globalVars.appArgs.configPath, "addons", "agenda" + addonHandler.ADDON_PENDINGINSTALL_SUFFIX, "globalPlugins", "agenda", "agenda.db")))
